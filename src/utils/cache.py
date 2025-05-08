from typing import Any, Optional
import aioredis
import json
import logging
from functools import wraps
from datetime import datetime

logger = logging.getLogger(__name__)

class CacheManager:
    def __init__(self, redis_url: str):
        self.redis = aioredis.from_url(redis_url)
        
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.error(f"Cache get error: {str(e)}")
            return None
            
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL."""
        try:
            value = json.dumps(value)
            await self.redis.set(key, value, ex=ttl)
            return True
        except Exception as e:
            logger.error(f"Cache set error: {str(e)}")
            return False
            
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        try:
            await self.redis.delete(key)
            return True
        except Exception as e:
            logger.error(f"Cache delete error: {str(e)}")
            return False
            
    async def clear_pattern(self, pattern: str) -> int:
        """Clear all keys matching pattern."""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {str(e)}")
            return 0

def cache_result(ttl: int = 3600):
    """Decorator to cache function results."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Generate cache key from function name and arguments
            key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = await cache_manager.get(key)
            if result is not None:
                return result
                
            # Execute function and cache result
            result = await func(*args, **kwargs)
            await cache_manager.set(key, result, ttl)
            return result
        return wrapper
    return decorator

# Initialize global cache manager
cache_manager = CacheManager("redis://redis:6379/0")
