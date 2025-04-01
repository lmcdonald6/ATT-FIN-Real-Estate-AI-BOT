"""
Cache module for efficient data storage and retrieval.
"""
import os
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

class Cache:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._data = {}
        self._metrics = {
            'api_calls': 0,
            'cache_hits': 0,
            'cache_misses': 0,
            'last_update': datetime.now().isoformat()
        }
        
        # Initialize cache directory
        self._init_cache_dir()
    
    def _init_cache_dir(self):
        """Initialize cache directory."""
        base_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'cache')
        os.makedirs(base_dir, exist_ok=True)
    
    def get(self, key: str, cache_type: str = 'property') -> Optional[Any]:
        """Get value from cache."""
        try:
            if key in self._data:
                self._metrics['cache_hits'] += 1
                return self._data[key]
            
            self._metrics['cache_misses'] += 1
            return None
        except Exception as e:
            self.logger.error(f"Error retrieving from cache: {e}")
            return None
    
    def set(self, key: str, value: Any, cache_type: str = 'property') -> bool:
        """Set value in cache."""
        try:
            self._data[key] = value
            self._metrics['last_update'] = datetime.now().isoformat()
            return True
        except Exception as e:
            self.logger.error(f"Error setting cache value: {e}")
            return False
    
    def track_api_call(self, api_name: str, response_time: float,
                      cache_hit: bool) -> None:
        """Track API call metrics."""
        if not cache_hit:
            self._metrics['api_calls'] += 1
    
    def get_api_calls_today(self) -> int:
        """Get number of API calls made today."""
        return self._metrics['api_calls']
    
    def get_health_metrics(self) -> Dict:
        """Get cache health metrics."""
        total_requests = (self._metrics['cache_hits'] +
                        self._metrics['cache_misses'])
        hit_ratio = (self._metrics['cache_hits'] / total_requests
                    if total_requests > 0 else 0.0)
        
        return {
            'api_calls': self._metrics['api_calls'],
            'cache_hits': self._metrics['cache_hits'],
            'cache_misses': self._metrics['cache_misses'],
            'hit_ratio': hit_ratio,
            'last_update': self._metrics['last_update']
        }
    
    def close(self) -> None:
        """Clean up resources."""
        self._data.clear()
        self._metrics['last_update'] = datetime.now().isoformat()
