"""Controller for Redfin data integration"""
import logging
import asyncio
from typing import Dict, List, Optional
from .redfin_scraper import RedfinScraper
from .redfin_cache_manager import RedfinCacheManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RedfinController:
    def __init__(self):
        """Initialize the Redfin controller"""
        self.cache_manager = RedfinCacheManager()
        self.scraper = RedfinScraper()
        
    async def get_properties(self, zip_code: str, filters: Optional[Dict] = None) -> List[Dict]:
        """Get properties for a ZIP code with optional filters"""
        try:
            # Extract filters
            max_price = filters.get('max_price') if filters else None
            min_beds = filters.get('min_beds') if filters else None
            
            # Try to get cached data first
            cached_data = self.cache_manager.get_cached_data(zip_code)
            if cached_data:
                logger.info(f"Using cached Redfin data for ZIP {zip_code}")
                return self._apply_filters(cached_data, filters)
                
            # Fetch fresh data from Redfin
            logger.info(f"Fetching fresh Redfin data for ZIP {zip_code}")
            properties = await self.scraper.search_properties(zip_code, max_price, min_beds)
            
            if properties:
                logger.info(f"Found {len(properties)} properties in ZIP {zip_code}")
                # Cache the results
                self.cache_manager.save_to_cache(zip_code, properties)
            else:
                logger.warning(f"No properties found in ZIP {zip_code}")
                
            return self._apply_filters(properties, filters) if properties else []
            
        except Exception as e:
            logger.error(f"Error getting Redfin properties: {str(e)}")
            return []
            
    def _apply_filters(self, properties: List[Dict], filters: Optional[Dict]) -> List[Dict]:
        """Apply filters to property list"""
        if not filters:
            return properties
            
        filtered = properties.copy()
        
        # Apply price filter
        if 'max_price' in filters:
            filtered = [p for p in filtered if p.get('price', float('inf')) <= filters['max_price']]
            
        # Apply beds filter
        if 'min_beds' in filters:
            filtered = [p for p in filtered if p.get('beds') and float(p.get('beds', 0)) >= filters['min_beds']]
            
        # Apply square footage filter
        if 'min_sqft' in filters:
            filtered = [p for p in filtered if p.get('square_feet') and p.get('square_feet', 0) >= filters['min_sqft']]
            
        # Apply days on market filter
        if 'min_days' in filters:
            filtered = [p for p in filtered if p.get('days_on_market', 0) >= filters['min_days']]
            
        # Apply price reduced filter
        if filters.get('only_reduced'):
            filtered = [p for p in filtered if p.get('price_reduced')]
            
        return filtered
        
    def get_cache_stats(self) -> Dict:
        """Get cache statistics"""
        return self.cache_manager.get_cache_stats()
        
    def clear_cache(self, zip_code: Optional[str] = None):
        """Clear cache for specific ZIP code or all cache"""
        self.cache_manager.clear_cache(zip_code)
        
    def stop(self):
        """Stop any running scraper operations"""
        if self.scraper:
            try:
                self.scraper._driver.quit()
            except:
                pass
