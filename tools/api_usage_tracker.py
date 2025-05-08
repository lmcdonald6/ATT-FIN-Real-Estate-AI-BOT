"""Track API usage and costs"""
import json
import os
from datetime import datetime, timedelta
from typing import Dict

class APIUsageTracker:
    """Track and manage API usage across all locations"""
    def __init__(self):
        self.usage_file = 'data/usage/attom_usage.json'
        self.monthly_limit = 400  # ATTOM API report limit
        
        # Ensure usage directory exists
        os.makedirs('data/usage', exist_ok=True)
        
        # Initialize or load usage data
        self.usage_data = self._load_usage_data()
    
    def _load_usage_data(self) -> Dict:
        """Load usage data from file"""
        try:
            if os.path.exists(self.usage_file):
                with open(self.usage_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            print(f"Error loading usage data: {str(e)}")
        
        # Default structure if file doesn't exist
        return {
            'current_month': datetime.now().strftime('%Y-%m'),
            'reports_used': 0,
            'reports_remaining': self.monthly_limit,
            'usage_by_location': {},
            'high_usage_locations': []  # Track locations with frequent requests
        }
    
    def _save_usage_data(self):
        """Save usage data to file"""
        try:
            with open(self.usage_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            print(f"Error saving usage data: {str(e)}")
    
    def record_api_call(self, location: str, report_count: int = 1):
        """Record an API call for a specific location"""
        current_month = datetime.now().strftime('%Y-%m')
        
        # Reset counter if new month
        if current_month != self.usage_data['current_month']:
            self.usage_data = {
                'current_month': current_month,
                'reports_used': 0,
                'reports_remaining': self.monthly_limit,
                'usage_by_location': {},
                'high_usage_locations': []
            }
        
        # Update global counters
        self.usage_data['reports_used'] += report_count
        self.usage_data['reports_remaining'] = max(0, self.monthly_limit - self.usage_data['reports_used'])
        
        # Update location-specific usage
        if location not in self.usage_data['usage_by_location']:
            self.usage_data['usage_by_location'][location] = {
                'reports_used': 0,
                'last_used': None,
                'cache_hits': 0
            }
        
        loc_data = self.usage_data['usage_by_location'][location]
        loc_data['reports_used'] += report_count
        loc_data['last_used'] = datetime.now().isoformat()
        
        # Update high usage locations list
        self._update_high_usage_locations(location)
        
        self._save_usage_data()
    
    def record_cache_hit(self, location: str):
        """Record a cache hit for a location"""
        if location in self.usage_data['usage_by_location']:
            self.usage_data['usage_by_location'][location]['cache_hits'] += 1
            self._save_usage_data()
    
    def _update_high_usage_locations(self, location: str):
        """Update list of high-usage locations"""
        usage = self.usage_data['usage_by_location'][location]['reports_used']
        
        # Consider a location "high usage" if it uses more than 5% of monthly limit
        if usage > (self.monthly_limit * 0.05):
            if location not in self.usage_data['high_usage_locations']:
                self.usage_data['high_usage_locations'].append(location)
    
    def get_monthly_summary(self) -> Dict:
        """Get summary of current month's usage"""
        return {
            'month': self.usage_data['current_month'],
            'reports_used': self.usage_data['reports_used'],
            'reports_remaining': self.usage_data['reports_remaining'],
            'high_usage_locations': self.usage_data['high_usage_locations']
        }
    
    def get_location_stats(self, location: str) -> Dict:
        """Get usage statistics for a specific location"""
        if location in self.usage_data['usage_by_location']:
            return self.usage_data['usage_by_location'][location]
        return {'reports_used': 0, 'last_used': None, 'cache_hits': 0}
    
    def should_use_attom(self, location: str, property_filters: Dict) -> bool:
        """Determine if ATTOM API should be used for this request"""
        # Always use ATTOM for high-priority requests
        if property_filters.get('prioritize_attom'):
            return True
        
        # Check remaining reports
        if self.usage_data['reports_remaining'] <= 0:
            return False
        
        # Check if location is high-usage
        if location in self.usage_data['high_usage_locations']:
            # For high-usage locations, only use ATTOM for specific cases
            return any([
                property_filters.get('investment_property'),
                property_filters.get('include_foreclosures'),
                property_filters.get('min_price', 0) > 1000000  # Luxury properties
            ])
        
        # For normal locations, use ATTOM more liberally
        return True

# Singleton instance
_tracker = None

def get_tracker() -> APIUsageTracker:
    """Get singleton instance of APIUsageTracker"""
    global _tracker
    if _tracker is None:
        _tracker = APIUsageTracker()
    return _tracker
