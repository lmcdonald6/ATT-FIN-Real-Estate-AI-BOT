"""Real Estate Controller - MVP with Local Caching"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional
from tools.attom_data_tool import AttomDataTool
from tools.property_analyzer import PropertyAnalyzer

logger = logging.getLogger(__name__)

class RealEstateController:
    def __init__(self):
        self.attom_tool = AttomDataTool()
        self.analyzer = PropertyAnalyzer()
        self.default_zip = "37208"  # Nashville area
        
        # Track API usage
        self.daily_api_calls = 0
        self.last_reset = datetime.now()
        self.max_daily_calls = 100  # Conservative limit for MVP
    
    async def search_properties(self, zip_code: str = None, filters: Dict = None) -> Dict:
        """Search for properties with optional filters"""
        try:
            # Reset daily counter if needed
            self._check_reset_counter()
            
            # Use default ZIP if none provided
            zip_code = zip_code or self.default_zip
            
            # Extract filter values
            property_type = filters.get('property_type') if filters else None
            min_beds = filters.get('min_beds') if filters else None
            max_price = filters.get('max_price') if filters else None
            
            # Get properties from ATTOM
            logger.info(f"Searching for properties in ZIP: {zip_code}")
            properties = await self.attom_tool.get_property_details(
                zip_code=zip_code,
                property_type=property_type,
                min_beds=min_beds,
                max_price=max_price
            )
            
            # Track API usage
            self.daily_api_calls += 1
            
            # Analyze results
            analysis = self._analyze_results(properties)
            
            return {
                'status': 'success',
                'properties': properties,
                'analysis': analysis,
                'analysis_date': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in property search: {str(e)}")
            return {
                'status': 'error',
                'message': str(e),
                'properties': [],
                'analysis_date': datetime.now().isoformat()
            }
    
    def _analyze_results(self, properties: List[Dict]) -> Dict:
        """Analyze property results for insights"""
        if not properties:
            return {}
        
        try:
            # Basic analysis
            total_properties = len(properties)
            total_value = sum(float(p.get('price', 0)) for p in properties if p.get('price'))
            avg_price = total_value / total_properties if total_properties > 0 else 0
            
            # Find investment opportunities
            investment_props = [p for p in properties if self._is_investment_opportunity(p)]
            
            return {
                'total_properties': total_properties,
                'average_price': avg_price,
                'investment_opportunities': len(investment_props),
                'price_range': {
                    'min': min((float(p.get('price', 0)) for p in properties if p.get('price')), default=0),
                    'max': max((float(p.get('price', 0)) for p in properties if p.get('price')), default=0)
                }
            }
            
        except Exception as e:
            logger.error(f"Error analyzing results: {str(e)}")
            return {}
    
    def _is_investment_opportunity(self, property_data: Dict) -> bool:
        """Basic check for investment potential"""
        try:
            # Simple criteria for MVP
            price = float(property_data.get('price', 0))
            sqft = float(property_data.get('sqft', 0))
            
            if price and sqft:
                price_per_sqft = price / sqft
                # Basic threshold for Nashville market
                return price_per_sqft < 200  # Adjust based on market
            
            return False
            
        except Exception:
            return False
    
    def _check_reset_counter(self):
        """Reset daily API counter if it's a new day"""
        now = datetime.now()
        if now.date() > self.last_reset.date():
            self.daily_api_calls = 0
            self.last_reset = now