import aiohttp
import logging
import json
import os
from datetime import datetime
from typing import Dict, List, Optional
from .mock_redfin_data import MockRedfinData

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RedfinDataTool:
    def __init__(self):
        """Initialize the Redfin data tool"""
        self.mock_data = MockRedfinData()  # Using mock data for MVP
        self.local_cache = "data/redfin_cache.json"
        self.load_cache()
        logger.debug("Initialized RedfinDataTool with mock data for MVP")

    def load_cache(self):
        """Load cached property data"""
        try:
            if os.path.exists(self.local_cache):
                with open(self.local_cache, 'r') as f:
                    self.cache = json.load(f)
            else:
                self.cache = {}
        except Exception as e:
            logger.error(f"Error loading cache: {str(e)}")
            self.cache = {}

    def save_cache(self):
        """Save property data to cache"""
        try:
            os.makedirs('data', exist_ok=True)
            with open(self.local_cache, 'w') as f:
                json.dump(self.cache, f)
        except Exception as e:
            logger.error(f"Error saving cache: {str(e)}")

    async def get_property_details(self, zip_code: str, property_type: str = None, min_beds: int = None, max_price: float = None) -> List[Dict]:
        """Get property details from mock Redfin data"""
        logger.debug(f"Starting Redfin property search for ZIP: {zip_code}")
        cache_key = f"{zip_code}_{property_type}_{min_beds}_{max_price}"
        
        # Check cache first
        if cache_key in self.cache:
            cached_data = self.cache[cache_key]
            if (datetime.now() - datetime.fromisoformat(cached_data['cache_date'])).days < 1:  # 24-hour cache
                logger.info(f"Using cached Redfin data for {zip_code}")
                return cached_data['data']

        try:
            # Generate mock data
            properties = self.mock_data.generate_properties(
                zip_code=zip_code,
                min_beds=min_beds,
                max_price=max_price
            )
            
            if properties:
                logger.info(f"Found {len(properties)} properties in Redfin matching criteria")
                
                # Cache the results
                self.cache[cache_key] = {
                    'data': properties,
                    'cache_date': datetime.now().isoformat()
                }
                self.save_cache()
                
                return properties
            else:
                logger.warning(f"No properties found in Redfin matching criteria")
                return []
                
        except Exception as e:
            logger.error(f"Error getting Redfin property details: {str(e)}")
            logger.debug("Exception details:", exc_info=True)
            return []

# Global tool instance
_tool = None

async def run(zip_code: str, property_type: str = None, min_beds: int = None, max_price: float = None) -> List[Dict]:
    """Run the Redfin Data tool"""
    global _tool
    
    if not zip_code:
        raise ValueError("ZIP code is required")
        
    _tool = RedfinDataTool()
    
    try:
        properties = await _tool.get_property_details(zip_code, property_type, min_beds, max_price)
        return properties
        
    except Exception as e:
        logger.error(f"Error running Redfin tool: {str(e)}")
        return []
    finally:
        _tool = None

async def stop():
    """Stop the Redfin Data tool"""
    global _tool
    if _tool:
        _tool = None
