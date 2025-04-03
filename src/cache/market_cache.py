"""
Caching layer for market analysis results with space optimization and cleanup.

This module provides Redis-based caching for market analysis data with:
- Automatic cache cleanup
- Memory usage monitoring
- Space-efficient storage
- Configurable retention policies
"""

import redis
import json
from typing import Dict, Any, Optional, List, Set
from datetime import datetime, timedelta
import hashlib
import zlib
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class MarketCache:
    """
    Space-optimized caching system for market analysis data.
    
    Features:
    - Compression for large datasets
    - Automatic cleanup of stale data
    - Memory usage monitoring
    - Configurable retention policies
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the cache with configuration.
        
        Args:
            config: Optional configuration dictionary with:
                - redis_host: Redis host (default: localhost)
                - redis_port: Redis port (default: 6379)
                - redis_db: Redis DB number (default: 0)
                - default_ttl: Default TTL in seconds (default: 3600)
                - max_memory_mb: Max memory usage in MB (default: 512)
                - compression_threshold: Size in bytes above which to compress (default: 1024)
        """
        self.config = config or {}
        try:
            self.redis_client = redis.Redis(
                host=self.config.get('redis_host', 'localhost'),
                port=self.config.get('redis_port', 6379),
                db=self.config.get('redis_db', 0)
            )
            self.redis_client.ping()
            logger.info("Successfully connected to Redis cache")
        except redis.ConnectionError as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

        self.default_ttl = self.config.get('default_ttl', 3600)
        self.max_memory_mb = self.config.get('max_memory_mb', 512)
        self.compression_threshold = self.config.get('compression_threshold', 1024)
        
        # Set Redis max memory policy
        if not self.config.get('testing', False):
            self.redis_client.config_set('maxmemory', f'{self.max_memory_mb}mb')
            self.redis_client.config_set('maxmemory-policy', 'allkeys-lru')
        
        # Initialize cleanup schedule
        self._schedule_cleanup()
    
    def _compress_data(self, data: Any) -> bytes:
        """Compress data if it exceeds threshold."""
        json_str = json.dumps(data, separators=(',', ':'))
        data_bytes = json_str.encode()
        if len(data_bytes) > self.compression_threshold:
            return zlib.compress(data_bytes)
        return data_bytes
    
    def _decompress_data(self, data: bytes) -> Any:
        """Decompress data if it was compressed."""
        try:
            decompressed = zlib.decompress(data).decode()
        except zlib.error:
            decompressed = data.decode()
        return json.loads(decompressed)
    
    def _schedule_cleanup(self) -> None:
        """Schedule periodic cache cleanup."""
        cleanup_interval = self.config.get('cleanup_interval', 3600)  # 1 hour
        logger.info(f"Scheduling cache cleanup every {cleanup_interval} seconds")
        # In a production environment, this would be handled by a task scheduler
        # For now, we'll just log the intention
    
    def _cleanup_expired(self) -> None:
        """Remove expired keys and optimize memory usage."""
        try:
            # Get memory usage
            info = self.redis_client.info()
            used_memory = int(info['used_memory']) / (1024 * 1024)  # Convert to MB
            
            if used_memory > self.max_memory_mb * 0.9:  # 90% threshold
                logger.warning(f"Cache memory usage high: {used_memory:.2f}MB/{self.max_memory_mb}MB")
                # Force cleanup of least recently used items
                self._cleanup_lru()
                
            logger.info(f"Current cache memory usage: {used_memory:.2f}MB")
        except redis.RedisError as e:
            logger.error(f"Error during cache cleanup: {e}")
    
    def _cleanup_lru(self) -> None:
        """Remove least recently used items when memory is high."""
        try:
            # Get all keys sorted by access time
            keys = self.redis_client.keys('*')
            if not keys:
                return
                
            # Remove 10% of least recently used keys
            num_to_remove = max(1, len(keys) // 10)
            keys_to_remove = keys[:num_to_remove]
            
            if keys_to_remove:
                self.redis_client.delete(*keys_to_remove)
                logger.info(f"Removed {len(keys_to_remove)} least recently used cache entries")
        except redis.RedisError as e:
            logger.error(f"Error during LRU cleanup: {e}")
    
    def _generate_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """Generate space-efficient cache key."""
        param_str = json.dumps(params, sort_keys=True, separators=(',', ':'))
        key_hash = hashlib.blake2b(param_str.encode(), digest_size=8).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get_market_analysis(self,
                          zip_code: str,
                          analysis_type: str,
                          params: Dict[str, Any]) -> Optional[Dict]:
        """Get cached market analysis with automatic decompression."""
        cache_key = self._generate_key(
            f"ma:{zip_code}:{analysis_type}",  # Shortened prefix
            params
        )
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = self._decompress_data(cached_data)
                logger.debug(f"Cache hit for {cache_key}")
                return data
            logger.debug(f"Cache miss for {cache_key}")
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Error retrieving market analysis: {e}")
            return None
    
    def cache_market_analysis(self,
                            zip_code: str,
                            analysis_type: str,
                            params: Dict[str, Any],
                            results: Dict[str, Any],
                            ttl: Optional[int] = None) -> None:
        """Cache market analysis with compression."""
        cache_key = self._generate_key(
            f"ma:{zip_code}:{analysis_type}",
            params
        )
        
        try:
            results['cached_at'] = datetime.now().isoformat()
            compressed_data = self._compress_data(results)
            
            self.redis_client.setex(
                cache_key,
                ttl or self.default_ttl,
                compressed_data
            )
            logger.debug(f"Cached market analysis for {cache_key}")
        except redis.RedisError as e:
            logger.error(f"Error caching market analysis: {e}")
    
    def get_property_data(self,
                         property_id: str,
                         source: str) -> Optional[Dict]:
        """Get cached property data with decompression."""
        cache_key = f"p:{source}:{property_id}"  # Shortened prefix
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = self._decompress_data(cached_data)
                logger.debug(f"Cache hit for property {property_id}")
                return data
            logger.debug(f"Cache miss for property {property_id}")
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Error retrieving property data: {e}")
            return None
    
    def cache_property_data(self,
                          property_id: str,
                          source: str,
                          data: Dict[str, Any],
                          ttl: Optional[int] = None) -> None:
        """Cache property data with compression."""
        cache_key = f"p:{source}:{property_id}"
        
        try:
            data['cached_at'] = datetime.now().isoformat()
            compressed_data = self._compress_data(data)
            
            self.redis_client.setex(
                cache_key,
                ttl or self.default_ttl,
                compressed_data
            )
            logger.debug(f"Cached property data for {property_id}")
        except redis.RedisError as e:
            logger.error(f"Error caching property data: {e}")
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get detailed cache statistics and memory usage."""
        try:
            info = self.redis_client.info()
            stats = {
                'memory_used_mb': int(info['used_memory']) / (1024 * 1024),
                'memory_peak_mb': int(info['used_memory_peak']) / (1024 * 1024),
                'memory_limit_mb': self.max_memory_mb,
                'total_keys': len(self.redis_client.keys('*')),
                'hit_rate': info['keyspace_hits'] / (
                    info['keyspace_hits'] + info['keyspace_misses']
                ) if info['keyspace_hits'] > 0 else 0,
                'uptime_seconds': info['uptime_in_seconds'],
                'compression_ratio': self._get_compression_ratio()
            }
            
            # Add key type statistics
            stats['key_counts'] = {
                'market_analysis': len(self.redis_client.keys('ma:*')),
                'property': len(self.redis_client.keys('p:*')),
                'neighborhood': len(self.redis_client.keys('n:*')),
                'trends': len(self.redis_client.keys('t:*'))
            }
            
            return stats
        except redis.RedisError as e:
            logger.error(f"Error getting cache stats: {e}")
            return {'error': str(e)}
    
    def _get_compression_ratio(self) -> float:
        """Calculate average compression ratio."""
        try:
            keys = self.redis_client.keys('*')
            if not keys:
                return 0.0
                
            sample_size = min(100, len(keys))  # Sample up to 100 keys
            total_ratio = 0.0
            count = 0
            
            for key in keys[:sample_size]:
                data = self.redis_client.get(key)
                if data:
                    original_size = len(self._decompress_data(data).encode())
                    compressed_size = len(data)
                    if original_size > 0:
                        total_ratio += compressed_size / original_size
                        count += 1
            
            return total_ratio / count if count > 0 else 0.0
        except redis.RedisError:
            return 0.0
    
    def get_neighborhood_score(self, zip_code: str) -> Optional[Dict]:
        """Get cached neighborhood score."""
        cache_key = f"n:{zip_code}"
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = self._decompress_data(cached_data)
                logger.debug(f"Cache hit for neighborhood score {zip_code}")
                return data
            logger.debug(f"Cache miss for neighborhood score {zip_code}")
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Error retrieving neighborhood score: {e}")
            return None
    
    def cache_neighborhood_score(self,
                               zip_code: str,
                               score_data: Dict[str, Any],
                               ttl: Optional[int] = None) -> None:
        """Cache neighborhood score."""
        cache_key = f"n:{zip_code}"
        
        try:
            score_data['cached_at'] = datetime.now().isoformat()
            compressed_data = self._compress_data(score_data)
            
            self.redis_client.setex(
                cache_key,
                ttl or self.default_ttl * 24,  # Neighborhood scores cached for longer
                compressed_data
            )
            logger.debug(f"Cached neighborhood score for {zip_code}")
        except redis.RedisError as e:
            logger.error(f"Error caching neighborhood score: {e}")
    
    def get_market_trends(self,
                         zip_code: str,
                         trend_type: str,
                         timeframe: str) -> Optional[Dict]:
        """Get cached market trends."""
        cache_key = f"t:{zip_code}:{trend_type}:{timeframe}"
        
        try:
            cached_data = self.redis_client.get(cache_key)
            if cached_data:
                data = self._decompress_data(cached_data)
                logger.debug(f"Cache hit for market trends {zip_code}")
                return data
            logger.debug(f"Cache miss for market trends {zip_code}")
            return None
        except (redis.RedisError, json.JSONDecodeError) as e:
            logger.error(f"Error retrieving market trends: {e}")
            return None
    
    def cache_market_trends(self,
                          zip_code: str,
                          trend_type: str,
                          timeframe: str,
                          trend_data: Dict[str, Any],
                          ttl: Optional[int] = None) -> None:
        """Cache market trends."""
        cache_key = f"t:{zip_code}:{trend_type}:{timeframe}"
        
        try:
            trend_data['cached_at'] = datetime.now().isoformat()
            compressed_data = self._compress_data(trend_data)
            
            self.redis_client.setex(
                cache_key,
                ttl or self.default_ttl * 12,  # Market trends cached for 12 hours
                compressed_data
            )
            logger.debug(f"Cached market trends for {zip_code}")
        except redis.RedisError as e:
            logger.error(f"Error caching market trends: {e}")
    
    def invalidate_zip_code(self, zip_code: str) -> None:
        """Invalidate all cached data for a ZIP code."""
        pattern = f"*:{zip_code}:*"
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
    
    def invalidate_property(self, property_id: str) -> None:
        """Invalidate cached data for a property."""
        pattern = f"p:*:{property_id}"
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
    
    def invalidate_analysis_type(self,
                               analysis_type: str,
                               zip_code: Optional[str] = None) -> None:
        """Invalidate cached analysis results by type."""
        pattern = f"ma:*:{analysis_type}:*"
        if zip_code:
            pattern = f"ma:{zip_code}:{analysis_type}:*"
            
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
