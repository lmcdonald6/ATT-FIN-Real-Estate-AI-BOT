"""Cache manager for Redfin property data"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class RedfinCacheManager:
    def __init__(self, cache_dir: str = 'data/redfin_cache'):
        """Initialize the cache manager"""
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(hours=12)  # Cache data for 12 hours
        os.makedirs(cache_dir, exist_ok=True)
        
    def _get_cache_file(self, zip_code: str) -> str:
        """Get cache file path for a ZIP code"""
        return os.path.join(self.cache_dir, f"{zip_code}.json")
        
    def get_cached_data(self, zip_code: str) -> Optional[List[Dict]]:
        """Get cached property data if available and not expired"""
        cache_file = self._get_cache_file(zip_code)
        
        if not os.path.exists(cache_file):
            return None
            
        try:
            with open(cache_file, 'r') as f:
                cache_data = json.load(f)
                
            # Check if cache is expired
            cache_time = datetime.fromisoformat(cache_data['timestamp'])
            if datetime.now() - cache_time > self.cache_duration:
                return None
                
            return cache_data['properties']
            
        except Exception as e:
            print(f"Error reading cache: {str(e)}")
            return None
            
    def save_to_cache(self, zip_code: str, properties: List[Dict]):
        """Save property data to cache"""
        cache_file = self._get_cache_file(zip_code)
        
        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'properties': properties
            }
            
            with open(cache_file, 'w') as f:
                json.dump(cache_data, f, indent=2)
                
        except Exception as e:
            print(f"Error saving to cache: {str(e)}")
            
    def clear_cache(self, zip_code: Optional[str] = None):
        """Clear cache for specific ZIP code or all cache"""
        if zip_code:
            cache_file = self._get_cache_file(zip_code)
            if os.path.exists(cache_file):
                os.remove(cache_file)
        else:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
                    
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        stats = {
            'total_cached_zips': 0,
            'total_properties': 0,
            'oldest_cache': None,
            'newest_cache': None
        }
        
        for file in os.listdir(self.cache_dir):
            if file.endswith('.json'):
                try:
                    with open(os.path.join(self.cache_dir, file), 'r') as f:
                        cache_data = json.load(f)
                        
                    stats['total_cached_zips'] += 1
                    stats['total_properties'] += len(cache_data['properties'])
                    
                    timestamp = datetime.fromisoformat(cache_data['timestamp'])
                    if not stats['oldest_cache'] or timestamp < stats['oldest_cache']:
                        stats['oldest_cache'] = timestamp
                    if not stats['newest_cache'] or timestamp > stats['newest_cache']:
                        stats['newest_cache'] = timestamp
                        
                except:
                    continue
                    
        return stats
