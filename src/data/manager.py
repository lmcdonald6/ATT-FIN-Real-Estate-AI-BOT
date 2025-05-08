"""
Data Manager
Handles caching and retrieval of property data
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
from pathlib import Path

class DataManager:
    """Manages property data caching and retrieval"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._cache = {}
        self._cache_ttl = timedelta(minutes=30)  # Cache data for 30 minutes
        
        # Initialize cache sections
        self._init_cache()
    
    def _init_cache(self):
        """Initialize cache sections"""
        self._cache = {
            'properties': {},      # Property details cache
            'market_data': {},     # Market trends cache
            'search_results': {},  # Search results cache
            'owner_data': {},      # Owner information cache
            'tax_data': {},        # Tax assessment cache
            'metrics': {           # Usage metrics
                'api_calls': 0,
                'cache_hits': 0,
                'cache_misses': 0
            }
        }
    
    def _get_cache_key(self, section: str, identifiers: List[str]) -> str:
        """Generate consistent cache key"""
        return f"{section}:{'_'.join(identifiers)}"
    
    def _is_cache_valid(self, cache_entry: Dict) -> bool:
        """Check if cache entry is still valid"""
        if not cache_entry or 'timestamp' not in cache_entry:
            return False
        
        age = datetime.now() - cache_entry['timestamp']
        return age < self._cache_ttl
    
    async def get_cached_search_results(self, city: str, state: str, zipcode: str) -> Optional[List[Dict]]:
        """Get cached property search results"""
        key = self._get_cache_key('search_results', [city, state, zipcode])
        entry = self._cache['search_results'].get(key)
        
        if entry and self._is_cache_valid(entry):
            self._cache['metrics']['cache_hits'] += 1
            return entry['data']
        
        self._cache['metrics']['cache_misses'] += 1
        return None
    
    async def cache_search_results(self, city: str, state: str, zipcode: str, results: List[Dict]):
        """Cache property search results"""
        key = self._get_cache_key('search_results', [city, state, zipcode])
        self._cache['search_results'][key] = {
            'data': results,
            'timestamp': datetime.now()
        }
    
    async def get_cached_market_data(self, zipcode: str) -> Optional[Dict]:
        """Get cached market data"""
        key = self._get_cache_key('market_data', [zipcode])
        entry = self._cache['market_data'].get(key)
        
        if entry and self._is_cache_valid(entry):
            self._cache['metrics']['cache_hits'] += 1
            return entry['data']
        
        self._cache['metrics']['cache_misses'] += 1
        return None
    
    async def cache_market_data(self, zipcode: str, data: Dict):
        """Cache market data"""
        key = self._get_cache_key('market_data', [zipcode])
        self._cache['market_data'][key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    async def get_cached_property_data(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get cached property data"""
        key = self._get_cache_key('properties', [address, zipcode])
        entry = self._cache['properties'].get(key)
        
        if entry and self._is_cache_valid(entry):
            self._cache['metrics']['cache_hits'] += 1
            return entry['data']
        
        self._cache['metrics']['cache_misses'] += 1
        return None
    
    async def cache_property_data(self, address: str, zipcode: str, data: Dict):
        """Cache property data"""
        key = self._get_cache_key('properties', [address, zipcode])
        self._cache['properties'][key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    async def get_cached_owner_data(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get cached owner data"""
        key = self._get_cache_key('owner_data', [address, zipcode])
        entry = self._cache['owner_data'].get(key)
        
        if entry and self._is_cache_valid(entry):
            self._cache['metrics']['cache_hits'] += 1
            return entry['data']
        
        self._cache['metrics']['cache_misses'] += 1
        return None
    
    async def cache_owner_data(self, address: str, zipcode: str, data: Dict):
        """Cache owner data"""
        key = self._get_cache_key('owner_data', [address, zipcode])
        self._cache['owner_data'][key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    async def get_cached_tax_data(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get cached tax data"""
        key = self._get_cache_key('tax_data', [address, zipcode])
        entry = self._cache['tax_data'].get(key)
        
        if entry and self._is_cache_valid(entry):
            self._cache['metrics']['cache_hits'] += 1
            return entry['data']
        
        self._cache['metrics']['cache_misses'] += 1
        return None
    
    async def cache_tax_data(self, address: str, zipcode: str, data: Dict):
        """Cache tax data"""
        key = self._get_cache_key('tax_data', [address, zipcode])
        self._cache['tax_data'][key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def get_metrics(self) -> Dict:
        """Get cache usage metrics"""
        total_requests = self._cache['metrics']['cache_hits'] + self._cache['metrics']['cache_misses']
        hit_rate = (self._cache['metrics']['cache_hits'] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'api_calls': self._cache['metrics']['api_calls'],
            'cache_hits': self._cache['metrics']['cache_hits'],
            'cache_misses': self._cache['metrics']['cache_misses'],
            'hit_rate': f"{hit_rate:.1f}%",
            'cache_entries': {
                'properties': len(self._cache['properties']),
                'market_data': len(self._cache['market_data']),
                'search_results': len(self._cache['search_results']),
                'owner_data': len(self._cache['owner_data']),
                'tax_data': len(self._cache['tax_data'])
            }
        }
    
    def increment_api_calls(self):
        """Increment API call counter"""
        self._cache['metrics']['api_calls'] += 1
