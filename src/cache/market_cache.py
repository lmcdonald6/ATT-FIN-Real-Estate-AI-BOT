"""Caching layer for market analysis results."""
import redis
import json
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import hashlib

class MarketCache:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.redis_client = redis.Redis(
            host=self.config.get('redis_host', 'localhost'),
            port=self.config.get('redis_port', 6379),
            db=self.config.get('redis_db', 0)
        )
        self.default_ttl = self.config.get('default_ttl', 3600)  # 1 hour
        
    def _generate_key(self, prefix: str, params: Dict[str, Any]) -> str:
        """Generate cache key from parameters."""
        # Sort parameters for consistent key generation
        param_str = json.dumps(params, sort_keys=True)
        key_hash = hashlib.md5(param_str.encode()).hexdigest()
        return f"{prefix}:{key_hash}"
    
    def get_market_analysis(self,
                          zip_code: str,
                          analysis_type: str,
                          params: Dict[str, Any]) -> Optional[Dict]:
        """Get cached market analysis results."""
        cache_key = self._generate_key(
            f"market_analysis:{zip_code}:{analysis_type}",
            params
        )
        
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
            
        return None
    
    def cache_market_analysis(self,
                            zip_code: str,
                            analysis_type: str,
                            params: Dict[str, Any],
                            results: Dict[str, Any],
                            ttl: Optional[int] = None) -> None:
        """Cache market analysis results."""
        cache_key = self._generate_key(
            f"market_analysis:{zip_code}:{analysis_type}",
            params
        )
        
        # Add timestamp to cached data
        results['cached_at'] = datetime.now().isoformat()
        
        self.redis_client.setex(
            cache_key,
            ttl or self.default_ttl,
            json.dumps(results)
        )
    
    def get_property_data(self,
                         property_id: str,
                         source: str) -> Optional[Dict]:
        """Get cached property data."""
        cache_key = f"property:{source}:{property_id}"
        
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
            
        return None
    
    def cache_property_data(self,
                          property_id: str,
                          source: str,
                          data: Dict[str, Any],
                          ttl: Optional[int] = None) -> None:
        """Cache property data."""
        cache_key = f"property:{source}:{property_id}"
        
        # Add timestamp to cached data
        data['cached_at'] = datetime.now().isoformat()
        
        self.redis_client.setex(
            cache_key,
            ttl or self.default_ttl,
            json.dumps(data)
        )
    
    def get_neighborhood_score(self, zip_code: str) -> Optional[Dict]:
        """Get cached neighborhood score."""
        cache_key = f"neighborhood_score:{zip_code}"
        
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
            
        return None
    
    def cache_neighborhood_score(self,
                               zip_code: str,
                               score_data: Dict[str, Any],
                               ttl: Optional[int] = None) -> None:
        """Cache neighborhood score."""
        cache_key = f"neighborhood_score:{zip_code}"
        
        # Add timestamp to cached data
        score_data['cached_at'] = datetime.now().isoformat()
        
        self.redis_client.setex(
            cache_key,
            ttl or self.default_ttl * 24,  # Neighborhood scores cached for longer
            json.dumps(score_data)
        )
    
    def get_market_trends(self,
                         zip_code: str,
                         trend_type: str,
                         timeframe: str) -> Optional[Dict]:
        """Get cached market trends."""
        cache_key = f"market_trends:{zip_code}:{trend_type}:{timeframe}"
        
        cached_data = self.redis_client.get(cache_key)
        if cached_data:
            return json.loads(cached_data)
            
        return None
    
    def cache_market_trends(self,
                          zip_code: str,
                          trend_type: str,
                          timeframe: str,
                          trend_data: Dict[str, Any],
                          ttl: Optional[int] = None) -> None:
        """Cache market trends."""
        cache_key = f"market_trends:{zip_code}:{trend_type}:{timeframe}"
        
        # Add timestamp to cached data
        trend_data['cached_at'] = datetime.now().isoformat()
        
        self.redis_client.setex(
            cache_key,
            ttl or self.default_ttl * 12,  # Market trends cached for 12 hours
            json.dumps(trend_data)
        )
    
    def invalidate_zip_code(self, zip_code: str) -> None:
        """Invalidate all cached data for a ZIP code."""
        pattern = f"*:{zip_code}:*"
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
    
    def invalidate_property(self, property_id: str) -> None:
        """Invalidate cached data for a property."""
        pattern = f"property:*:{property_id}"
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
    
    def invalidate_analysis_type(self,
                               analysis_type: str,
                               zip_code: Optional[str] = None) -> None:
        """Invalidate cached analysis results by type."""
        pattern = f"market_analysis:*:{analysis_type}:*"
        if zip_code:
            pattern = f"market_analysis:{zip_code}:{analysis_type}:*"
            
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        stats = {
            'total_keys': len(self.redis_client.keys('*')),
            'memory_used': self.redis_client.info()['used_memory_human'],
            'hit_rate': self.redis_client.info()['keyspace_hits'] / (
                self.redis_client.info()['keyspace_hits'] +
                self.redis_client.info()['keyspace_misses']
            ) if self.redis_client.info()['keyspace_hits'] > 0 else 0,
            'uptime': self.redis_client.info()['uptime_in_seconds']
        }
        
        # Count keys by type
        stats['key_counts'] = {
            'market_analysis': len(self.redis_client.keys('market_analysis:*')),
            'property': len(self.redis_client.keys('property:*')),
            'neighborhood_score': len(self.redis_client.keys('neighborhood_score:*')),
            'market_trends': len(self.redis_client.keys('market_trends:*'))
        }
        
        return stats
