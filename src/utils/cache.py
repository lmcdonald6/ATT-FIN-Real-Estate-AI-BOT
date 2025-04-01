from typing import Any, Optional
import time
import json
import os
from threading import Lock

class Cache:
    def __init__(self, cache_dir: str = "cache"):
        self.cache_dir = cache_dir
        self.memory_cache = {}
        self.lock = Lock()
        os.makedirs(cache_dir, exist_ok=True)

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        # Try memory cache first
        with self.lock:
            if key in self.memory_cache:
                value, expiry = self.memory_cache[key]
                if expiry > time.time():
                    return value
                else:
                    del self.memory_cache[key]

        # Try disk cache
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_file):
            try:
                with open(cache_file, 'r') as f:
                    data = json.load(f)
                    if data['expiry'] > time.time():
                        # Update memory cache
                        with self.lock:
                            self.memory_cache[key] = (data['value'], data['expiry'])
                        return data['value']
                    else:
                        os.remove(cache_file)
            except Exception as e:
                print(f"Error reading cache: {str(e)}")

        return None

    def set(self, key: str, value: Any, expire: int = 3600) -> None:
        """Set value in cache with expiration in seconds"""
        expiry = time.time() + expire

        # Update memory cache
        with self.lock:
            self.memory_cache[key] = (value, expiry)

        # Update disk cache
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        try:
            with open(cache_file, 'w') as f:
                json.dump({
                    'value': value,
                    'expiry': expiry
                }, f)
        except Exception as e:
            print(f"Error writing cache: {str(e)}")

    def delete(self, key: str) -> None:
        """Delete value from cache"""
        # Remove from memory cache
        with self.lock:
            if key in self.memory_cache:
                del self.memory_cache[key]

        # Remove from disk cache
        cache_file = os.path.join(self.cache_dir, f"{key}.json")
        if os.path.exists(cache_file):
            try:
                os.remove(cache_file)
            except Exception as e:
                print(f"Error deleting cache: {str(e)}")

    def clear(self) -> None:
        """Clear all cache"""
        # Clear memory cache
        with self.lock:
            self.memory_cache.clear()

        # Clear disk cache
        try:
            for file in os.listdir(self.cache_dir):
                if file.endswith('.json'):
                    os.remove(os.path.join(self.cache_dir, file))
        except Exception as e:
            print(f"Error clearing cache: {str(e)}")

    def cleanup(self) -> None:
        """Remove expired cache entries"""
        current_time = time.time()

        # Clean memory cache
        with self.lock:
            expired_keys = [
                key for key, (_, expiry) in self.memory_cache.items()
                if expiry <= current_time
            ]
            for key in expired_keys:
                del self.memory_cache[key]

        # Clean disk cache
        try:
            for file in os.listdir(self.cache_dir):
                if not file.endswith('.json'):
                    continue

                cache_file = os.path.join(self.cache_dir, file)
                try:
                    with open(cache_file, 'r') as f:
                        data = json.load(f)
                        if data['expiry'] <= current_time:
                            os.remove(cache_file)
                except Exception as e:
                    print(f"Error cleaning cache file {file}: {str(e)}")
        except Exception as e:
            print(f"Error cleaning cache directory: {str(e)}")

    def get_stats(self) -> dict:
        """Get cache statistics"""
        memory_size = len(self.memory_cache)
        disk_size = len([f for f in os.listdir(self.cache_dir) if f.endswith('.json')])
        
        return {
            'memory_entries': memory_size,
            'disk_entries': disk_size,
            'cache_dir': self.cache_dir
        }
