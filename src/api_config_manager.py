"""API Configuration Manager for Real Estate AI Bot"""
import os
from typing import Dict, Optional
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class APIConfigManager:
    """Manages API configurations and rate limiting for real estate data sources"""
    
    def __init__(self):
        load_dotenv()
        self._init_attom_config()
        self._init_redfin_config()
        self._init_rate_limits()
        
    def _init_attom_config(self) -> None:
        """Initialize ATTOM API configuration"""
        self.attom_config = {
            'api_key': os.getenv('ATTOM_API_KEY'),
            'base_url': os.getenv('ATTOM_API_BASE_URL'),
            'rate_limit': int(os.getenv('ATTOM_RATE_LIMIT', 100)),
            'headers': {
                'apikey': os.getenv('ATTOM_API_KEY'),
                'accept': 'application/json'
            }
        }
        
    def _init_redfin_config(self) -> None:
        """Initialize Redfin API configuration"""
        self.redfin_config = {
            'base_url': os.getenv('REDFIN_API_BASE_URL'),
            'headers': {
                'User-Agent': os.getenv('REDFIN_USER_AGENT'),
                'Accept': 'application/json'
            }
        }
        
    def _init_rate_limits(self) -> None:
        """Initialize rate limiting configuration"""
        self.rate_limits = {
            'timeout': int(os.getenv('REQUEST_TIMEOUT', 30)),
            'max_retries': int(os.getenv('MAX_RETRIES', 3)),
            'retry_delay': int(os.getenv('RETRY_DELAY', 5))
        }
        self._request_timestamps = []
        
    def get_attom_headers(self) -> Dict:
        """Get ATTOM API headers with current API key"""
        return self.attom_config['headers']
        
    def get_redfin_headers(self) -> Dict:
        """Get Redfin API headers"""
        return self.redfin_config['headers']
        
    def get_api_urls(self) -> Dict:
        """Get base URLs for all APIs"""
        return {
            'attom': self.attom_config['base_url'],
            'redfin': self.redfin_config['base_url']
        }
        
    def check_rate_limit(self) -> bool:
        """Check if current request would exceed rate limit"""
        now = datetime.now()
        # Remove timestamps older than 1 minute
        self._request_timestamps = [
            ts for ts in self._request_timestamps
            if now - ts < timedelta(minutes=1)
        ]
        
        if len(self._request_timestamps) >= self.attom_config['rate_limit']:
            logger.warning("Rate limit reached. Waiting before next request.")
            return False
            
        self._request_timestamps.append(now)
        return True
        
    def get_retry_settings(self) -> Dict:
        """Get retry configuration settings"""
        return {
            'timeout': self.rate_limits['timeout'],
            'max_retries': self.rate_limits['max_retries'],
            'retry_delay': self.rate_limits['retry_delay']
        }
        
    def validate_api_keys(self) -> bool:
        """Validate that all required API keys are present"""
        if not self.attom_config['api_key']:
            logger.error("ATTOM API key not found in environment")
            return False
            
        return True
        
    def get_search_parameters(self) -> Dict:
        """Get configured search parameters"""
        return {
            'max_price': int(os.getenv('MAX_PRICE', 400000)),
            'min_price': int(os.getenv('MIN_PRICE', 50000)),
            'property_type': os.getenv('DEFAULT_PROPERTY_TYPE', 'SFR'),
            'search_radius': int(os.getenv('SEARCH_RADIUS', 1)),
            'max_results': int(os.getenv('MAX_RESULTS_PER_QUERY', 50))
        }
        
    def get_lead_scoring_thresholds(self) -> Dict:
        """Get configured lead scoring thresholds"""
        return {
            'high_probability': int(os.getenv('HIGH_PROBABILITY_LEAD', 70)),
            'market_opportunity': float(os.getenv('MARKET_OPPORTUNITY_THRESHOLD', 0.15)),
            'high_demand': int(os.getenv('HIGH_DEMAND_AREA_THRESHOLD', 100)),
            'price_drop': float(os.getenv('PRICE_DROP_THRESHOLD', 0.10))
        }
