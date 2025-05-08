"""Real Estate Controller - Handles property search and data management"""
import logging
from typing import Dict, List
from .property_data_service import PropertyDataService
from .query_processor import QueryProcessor

logger = logging.getLogger(__name__)

class RealEstateController:
    def __init__(self):
        self.data_service = PropertyDataService()
        self.query_processor = QueryProcessor()
        self.default_zips = ['37215', '37205', '37027']  # Nashville prime areas
    
    async def search_properties(self, filters: Dict = None) -> Dict:
        """Search for properties using the data service"""
        try:
            # Parse natural language query if present
            if filters and 'query' in filters:
                filters = self.query_processor.parse_query(filters['query'])
            
            # Use specified ZIP codes or defaults
            zip_codes = filters.get('zip_codes') or self.default_zips
            
            all_properties = []
            for zip_code in zip_codes:
                try:
                    properties = await self.data_service.search_properties(zip_code, filters)
                    if properties:
                        all_properties.extend(properties)
                except Exception as e:
                    logger.error(f"Error searching {zip_code}: {str(e)}")
                    continue
            
            # Sort and analyze results
            if all_properties:
                analysis = self.query_processor.analyze_properties(all_properties, filters)
                return {
                    'status': 'success',
                    'properties': analysis.get('deals', []),
                    'total': len(all_properties),
                    'avg_price': analysis.get('avg_price')
                }
            else:
                return {
                    'status': 'success',
                    'properties': [],
                    'message': 'No properties found matching your criteria.'
                }
                
        except Exception as e:
            logger.error(f"Error in search_properties: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
