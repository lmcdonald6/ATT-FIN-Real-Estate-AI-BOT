"""
Zillow data source plugin for property data integration.
"""
import asyncio
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import aiohttp
import pandas as pd

from src.core.plugin_system import DataSourcePlugin
from src.utils.cache import Cache

logger = logging.getLogger(__name__)

class ZillowDataSource(DataSourcePlugin):
    """Plugin for fetching and processing Zillow property data"""
    
    def __init__(self):
        self.api_key = None
        self.cache = Cache()
        self.rate_limiter = None
        self.session = None
        
    def initialize(self, config: Dict) -> bool:
        """Initialize the plugin with configuration"""
        try:
            self.api_key = config['api_key']
            self.cache.set_ttl(config.get('cache_ttl', 3600))
            self.rate_limiter = asyncio.Semaphore(config.get('max_requests_per_second', 5))
            self.session = aiohttp.ClientSession(
                headers={'Authorization': f'Bearer {self.api_key}'}
            )
            return True
        except Exception as e:
            logger.error(f"Failed to initialize Zillow plugin: {str(e)}")
            return False
            
    def get_capabilities(self) -> List[str]:
        """Get list of plugin capabilities"""
        return ['property_search', 'property_details', 'market_trends']
        
    def process(self, data: Dict) -> Dict:
        """Process property data"""
        try:
            # Convert data to standard format
            processed = {
                'property_id': data.get('zpid'),
                'address': {
                    'street': data.get('address', {}).get('streetAddress'),
                    'city': data.get('address', {}).get('city'),
                    'state': data.get('address', {}).get('state'),
                    'zip': data.get('address', {}).get('zipcode')
                },
                'price': data.get('price'),
                'square_feet': data.get('livingArea'),
                'bedrooms': data.get('bedrooms'),
                'bathrooms': data.get('bathrooms'),
                'year_built': data.get('yearBuilt'),
                'lot_size': data.get('lotSize'),
                'property_type': data.get('propertyType'),
                'zestimate': data.get('zestimate'),
                'rent_zestimate': data.get('rentZestimate'),
                'last_updated': datetime.now().isoformat()
            }
            
            return processed
        except Exception as e:
            logger.error(f"Error processing Zillow data: {str(e)}")
            return data
            
    async def fetch_data(self, query: Dict) -> Dict:
        """Fetch property data from Zillow"""
        cache_key = f"zillow_{query.get('property_id', '')}_{query.get('address', '')}"
        
        # Check cache first
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
            
        async with self.rate_limiter:
            try:
                if 'property_id' in query:
                    endpoint = f"/api/v1/properties/{query['property_id']}"
                else:
                    # Search by address
                    address = query['address']
                    endpoint = f"/api/v1/properties/search?address={address}"
                    
                async with self.session.get(f"https://api.zillow.com{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        processed_data = self.process(data)
                        self.cache.set(cache_key, processed_data)
                        return processed_data
                    else:
                        logger.error(f"Zillow API error: {response.status}")
                        return {}
                        
            except Exception as e:
                logger.error(f"Error fetching from Zillow: {str(e)}")
                return {}
                
    def validate_data(self, data: Dict) -> bool:
        """Validate property data format"""
        required_fields = ['property_id', 'address', 'price']
        return all(field in data for field in required_fields)
        
    async def get_market_trends(self, zip_code: str, months: int = 12) -> Dict:
        """Get market trends for a zip code"""
        cache_key = f"zillow_trends_{zip_code}_{months}"
        
        cached_data = self.cache.get(cache_key)
        if cached_data:
            return cached_data
            
        async with self.rate_limiter:
            try:
                endpoint = f"/api/v1/market-trends?zip={zip_code}&months={months}"
                async with self.session.get(f"https://api.zillow.com{endpoint}") as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # Process trend data
                        df = pd.DataFrame(data['trends'])
                        df['date'] = pd.to_datetime(df['date'])
                        df = df.set_index('date')
                        
                        trends = {
                            'median_price': df['median_price'].to_dict(),
                            'price_change': df['median_price'].pct_change().fillna(0).to_dict(),
                            'inventory': df['inventory'].to_dict(),
                            'days_on_market': df['days_on_market'].to_dict(),
                            'last_updated': datetime.now().isoformat()
                        }
                        
                        self.cache.set(cache_key, trends)
                        return trends
                    else:
                        logger.error(f"Zillow API error: {response.status}")
                        return {}
                        
            except Exception as e:
                logger.error(f"Error fetching market trends: {str(e)}")
                return {}
                
    async def cleanup(self):
        """Cleanup resources"""
        if self.session:
            await self.session.close()
            
    def __del__(self):
        """Cleanup on deletion"""
        if self.session and not self.session.closed:
            asyncio.create_task(self.cleanup())
