"""ATTOM API integration for property data enrichment"""
import os
import aiohttp
import json
import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from .api_usage_tracker import get_tracker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AttomDataTool:
    """ATTOM API client for property data enrichment"""
    def __init__(self):
        self.api_key = "e5bb16c669ddbe7c803b7779fba4acd7"  # MVP: Direct key, will move to .env post-MVP
        self.base_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"
        self.tracker = get_tracker()
        
        # Cache settings
        self.cache_file = 'data/cache/attom_cache.json'
        self.cache_duration = timedelta(hours=24)
        self.cache = self._load_cache()
        
        # Create cache directory
        os.makedirs('data/cache', exist_ok=True)
    
    async def get_property_details(
        self, 
        zip_code: str, 
        property_type: Optional[str] = None,
        min_beds: Optional[int] = None,
        max_price: Optional[float] = None
    ) -> List[Dict]:
        """Get property details from ATTOM API"""
        try:
            # Check cache first
            filters = {
                'property_type': property_type,
                'min_beds': min_beds,
                'max_price': max_price
            }
            cache_key = self._cache_key(zip_code, filters)
            
            if self._is_cache_valid(cache_key):
                logger.info(f"Using cached ATTOM data for {zip_code}")
                return self.cache[cache_key]['data']
            
            # Check API usage before making request
            usage = self.tracker.get_monthly_summary()
            if usage['reports_remaining'] <= 0:
                logger.warning("Monthly ATTOM API limit reached!")
                return []
            
            # Build API request
            headers = {
                'apikey': self.api_key,
                'accept': 'application/json'
            }
            
            # Map property types to ATTOM format
            attom_property_types = {
                'Single Family': 'SFR',
                'Townhouse': 'TOWNHOUSE',
                'Condo': 'CONDO',
                'Multi-Family': 'MFR'
            }
            
            # Build query parameters
            params = {
                'postalcode': zip_code,
                'pageSize': 25,  # Limit results per request
                'propertytype': attom_property_types.get(property_type, 'SFR,CONDO,MFR'),
            }
            
            # Add optional filters
            if min_beds:
                params['minBeds'] = min_beds
            if max_price:
                params['maxAssessedValue'] = max_price
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.base_url}/property/basicprofile",
                    headers=headers,
                    params=params
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        properties = self._parse_attom_response(data)
                        
                        # Cache the results
                        self.cache[cache_key] = {
                            'data': properties,
                            'timestamp': datetime.now().isoformat()
                        }
                        self._save_cache()
                        
                        # Track API usage
                        self.tracker.track_request(
                            endpoint='property/basicprofile',
                            status=response.status,
                            zip_code=zip_code
                        )
                        
                        return properties
                    else:
                        logger.error(f"ATTOM API error: {response.status}")
                        error_data = await response.text()
                        logger.error(f"Error details: {error_data}")
                        return []
                        
        except Exception as e:
            logger.error(f"Error fetching ATTOM data: {str(e)}")
            return []
    
    def _cache_key(self, zip_code: str, filters: Dict) -> str:
        """Generate cache key from search parameters"""
        filter_str = json.dumps(filters, sort_keys=True) if filters else ''
        return f"{zip_code}_{filter_str}"
    
    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self.cache:
            return False
        
        timestamp = datetime.fromisoformat(self.cache[key]['timestamp'])
        age = datetime.now() - timestamp
        return age < self.cache_duration
    
    def _load_cache(self) -> Dict:
        """Load cached ATTOM data"""
        try:
            if os.path.exists(self.cache_file):
                with open(self.cache_file, 'r') as f:
                    return json.load(f)
        except Exception as e:
            logger.error(f"Error loading ATTOM cache: {str(e)}")
        return {}
    
    def _save_cache(self):
        """Save ATTOM data to cache"""
        try:
            with open(self.cache_file, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving ATTOM cache: {str(e)}")
    
    def _parse_attom_response(self, response: Dict) -> List[Dict]:
        """Parse ATTOM API response into standardized format"""
        try:
            properties = []
            for prop in response.get('property', []):
                # Extract address components
                address = prop.get('address', {})
                
                # Extract assessment info
                assessment = prop.get('assessment', {})
                
                # Extract building info
                building = prop.get('building', {})
                
                # Extract lot info
                lot = prop.get('lot', {})
                
                # Extract owner info
                owner = prop.get('owner', {})
                
                # Extract sale info
                sale = prop.get('sale', {})
                
                # Build standardized property data
                property_data = {
                    'address': f"{address.get('streetNumber', '')} {address.get('streetName', '')} {address.get('streetSuffix', '')}",
                    'zip_code': address.get('zipCode'),
                    'price': assessment.get('totalAssessedValue'),
                    'beds': building.get('rooms', {}).get('beds'),
                    'baths': building.get('rooms', {}).get('bathsFull'),
                    'square_feet': building.get('size', {}).get('grossSize'),
                    'year_built': building.get('yearBuilt'),
                    'lot_size': lot.get('lotSize1'),
                    'owner_occupied': owner.get('ownerOccupied', '').lower() == 'yes',
                    'last_sale_date': sale.get('saleTransDate'),
                    'last_sale_price': sale.get('saleAmt'),
                    'property_type': self._map_attom_property_type(prop.get('propertyType')),
                    'data_source': 'attom'
                }
                
                # Only add properties with essential data
                if all(property_data[k] is not None for k in ['address', 'price', 'beds']):
                    properties.append(property_data)
            
            return properties
            
        except Exception as e:
            logger.error(f"Error parsing ATTOM response: {str(e)}")
            return []
    
    def _map_attom_property_type(self, attom_type: str) -> str:
        """Map ATTOM property types to our standard types"""
        type_mapping = {
            'SFR': 'Single Family',
            'TOWNHOUSE': 'Townhouse',
            'CONDO': 'Condo',
            'MFR': 'Multi-Family'
        }
        return type_mapping.get(attom_type, 'Single Family')
