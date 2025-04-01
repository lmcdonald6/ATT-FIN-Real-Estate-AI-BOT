"""
Persistent storage system for property data.
Builds a local database of property information over time.
"""
import json
import os
import logging
from typing import Dict, Optional, List
from datetime import datetime
from pathlib import Path

class PropertyStorage:
    def __init__(self, base_dir: str = "data"):
        self.logger = logging.getLogger(__name__)
        self.base_dir = Path(base_dir)
        
        # Create directory structure
        self._init_storage()
        
        # Track stored properties
        self.property_index = self._load_index()
        
        # Initialize storage manager for caching
        self.storage_manager = StorageManager()
    
    def _init_storage(self):
        """Initialize storage directory structure."""
        # Main data directory
        self.base_dir.mkdir(exist_ok=True)
        
        # Subdirectories for different data types
        (self.base_dir / "properties").mkdir(exist_ok=True)
        (self.base_dir / "market").mkdir(exist_ok=True)
        (self.base_dir / "foreclosures").mkdir(exist_ok=True)
        
        # Property index file
        if not (self.base_dir / "property_index.json").exists():
            self._save_index({})
    
    def _get_property_key(self, address: str, zip_code: str) -> str:
        """Generate a unique key for a property."""
        # Clean address for filesystem
        clean_address = "".join(c if c.isalnum() else "_" for c in address.lower())
        return f"{clean_address}_{zip_code}"
    
    def _load_index(self) -> Dict:
        """Load property index from disk."""
        try:
            with open(self.base_dir / "property_index.json", "r") as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
    
    def _save_index(self, index: Dict):
        """Save property index to disk."""
        with open(self.base_dir / "property_index.json", "w") as f:
            json.dump(index, f, indent=2)
    
    def store_property(self, address: str, zip_code: str, data: Dict) -> bool:
        """
        Store property data to disk.
        Returns True if successful, False otherwise.
        """
        try:
            prop_key = self._get_property_key(address, zip_code)
            
            # Update property data
            prop_file = self.base_dir / "properties" / f"{prop_key}.json"
            data["last_updated"] = datetime.now().isoformat()
            
            with open(prop_file, "w") as f:
                json.dump(data, f, indent=2)
            
            # Update index
            self.property_index[prop_key] = {
                "address": address,
                "zip_code": zip_code,
                "last_updated": data["last_updated"],
                "property_type": data.get("property_type", "Unknown"),
                "has_foreclosure": bool(data.get("foreclosure")),
                "file_path": str(prop_file)
            }
            self._save_index(self.property_index)
            
            # If foreclosure data exists, store separately
            if data.get("foreclosure"):
                foreclosure_file = self.base_dir / "foreclosures" / f"{prop_key}.json"
                with open(foreclosure_file, "w") as f:
                    json.dump({
                        "address": address,
                        "zip_code": zip_code,
                        "foreclosure_data": data["foreclosure"],
                        "last_updated": data["last_updated"]
                    }, f, indent=2)
            
            # Cache property data
            self.storage_manager.set(prop_key, data, expire_hours=24)
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error storing property data: {e}")
            return False
    
    def get_property(self, address: str, zip_code: str) -> Optional[Dict]:
        """
        Retrieve property data from storage.
        Returns None if property not found.
        """
        try:
            prop_key = self._get_property_key(address, zip_code)
            return self.get_property_by_key(prop_key)
            
        except Exception as e:
            self.logger.error(f"Error retrieving property data: {e}")
            return None
    
    def get_property_by_key(self, prop_key: str) -> Optional[Dict]:
        """
        Retrieve property data from storage using its key.
        Returns None if property not found.
        """
        try:
            # Check cache first
            cached_data = self.storage_manager.get(prop_key)
            if cached_data:
                return cached_data
            
            prop_info = self.property_index.get(prop_key)
            
            if prop_info and os.path.exists(prop_info["file_path"]):
                with open(prop_info["file_path"], "r") as f:
                    return json.load(f)
            
            return None
            
        except Exception as e:
            self.logger.error(f"Error retrieving property data by key: {e}")
            return None
    
    def get_foreclosures(self, zip_code: Optional[str] = None) -> List[Dict]:
        """Get all stored foreclosure data, optionally filtered by ZIP code."""
        foreclosures = []
        foreclosure_dir = self.base_dir / "foreclosures"
        
        try:
            for file in foreclosure_dir.glob("*.json"):
                with open(file, "r") as f:
                    data = json.load(f)
                    if not zip_code or data["zip_code"] == zip_code:
                        foreclosures.append(data)
            
            return foreclosures
            
        except Exception as e:
            self.logger.error(f"Error retrieving foreclosure data: {e}")
            return []
    
    def search_properties(self, zip_code: Optional[str] = None,
                        property_type: Optional[str] = None,
                        has_foreclosure: Optional[bool] = None) -> List[str]:
        """
        Search stored properties by criteria.
        Returns list of property keys matching criteria.
        """
        matching_keys = []
        
        for key, info in self.property_index.items():
            matches = True
            
            if zip_code and info["zip_code"] != zip_code:
                matches = False
            if property_type and info["property_type"] != property_type:
                matches = False
            if has_foreclosure is not None and info["has_foreclosure"] != has_foreclosure:
                matches = False
            
            if matches:
                matching_keys.append(key)
        
        return matching_keys


"""
Storage manager for property data caching.
"""
import logging
from typing import Any, Dict, Optional
from datetime import datetime, timedelta

class StorageManager:
    """
    Manages data storage and caching.
    Implements in-memory storage with TTL.
    """
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._storage = {}
        self._expiry = {}
    
    def get(self, key: str) -> Optional[Any]:
        """
        Get value from storage if not expired.
        Returns None if key not found or expired.
        """
        try:
            # Check if key exists and not expired
            if key in self._storage:
                if self._is_expired(key):
                    self._remove(key)
                    return None
                return self._storage[key]
            return None
            
        except Exception as e:
            self.logger.error(f"Error getting from storage: {e}")
            return None
    
    def set(self,
            key: str,
            value: Any,
            expire_hours: int = 24) -> bool:
        """
        Store value with expiration time.
        Returns True if successful.
        """
        try:
            self._storage[key] = value
            self._expiry[key] = datetime.now() + timedelta(hours=expire_hours)
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting storage: {e}")
            return False
    
    def delete(self, key: str) -> bool:
        """
        Delete key from storage.
        Returns True if key was found and deleted.
        """
        try:
            if key in self._storage:
                self._remove(key)
                return True
            return False
            
        except Exception as e:
            self.logger.error(f"Error deleting from storage: {e}")
            return False
    
    def clear(self) -> bool:
        """Clear all storage."""
        try:
            self._storage.clear()
            self._expiry.clear()
            return True
            
        except Exception as e:
            self.logger.error(f"Error clearing storage: {e}")
            return False
    
    def get_stats(self) -> Dict:
        """Get storage statistics."""
        try:
            total = len(self._storage)
            expired = sum(1 for k in self._storage if self._is_expired(k))
            return {
                "total_keys": total,
                "active_keys": total - expired,
                "expired_keys": expired
            }
            
        except Exception as e:
            self.logger.error(f"Error getting storage stats: {e}")
            return {}
    
    def _is_expired(self, key: str) -> bool:
        """Check if key is expired."""
        if key not in self._expiry:
            return True
        return datetime.now() > self._expiry[key]
    
    def _remove(self, key: str):
        """Remove key from storage and expiry."""
        self._storage.pop(key, None)
        self._expiry.pop(key, None)
