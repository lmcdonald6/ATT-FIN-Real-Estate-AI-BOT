"""Real estate bot with hybrid data approach (Mock Redfin + ATTOM API)"""
import asyncio
from typing import Dict, List, Optional
from tools.query_processor import QueryProcessor
from tools.mock_redfin_data import MockRedfinData
from tools.attom_data_tool import AttomDataTool
from tools.api_usage_tracker import get_tracker
from utils.logging_config import setup_logging

# Configure logging with rotation
logger = setup_logging(app_name="real_estate_bot")

class RealEstateBot:
    """Real estate bot using hybrid data approach"""
    def __init__(self):
        self.query_processor = QueryProcessor()
        self.mock_redfin = MockRedfinData()
        self.attom_tool = AttomDataTool()
        self.api_tracker = get_tracker()
        
        # Cache settings
        self._property_cache = {}
    
    async def search_properties(self, query: str) -> Dict:
        """Search properties using natural language query"""
        try:
            # Parse query into structured filters
            filters = self.query_processor.parse_query(query)
            if 'error' in filters:
                return {'error': filters['error']}
            
            # Get properties from both sources
            properties = []
            
            # Get mock Redfin data first
            for zip_code in filters['zip_codes']:
                mock_props = self.mock_redfin.get_properties(
                    zip_code=zip_code,
                    state=filters['state'],
                    property_type=filters.get('property_type'),
                    min_beds=filters.get('min_beds'),
                    max_price=filters.get('max_price'),
                    area_type=filters.get('area_type')
                )
                properties.extend(mock_props)
            
            # Enrich with ATTOM data if available
            if self._should_use_attom(filters):
                for zip_code in filters['zip_codes']:
                    attom_props = await self.attom_tool.get_property_details(
                        zip_code=zip_code,
                        property_type=filters.get('property_type'),
                        min_beds=filters.get('min_beds'),
                        max_price=filters.get('max_price')
                    )
                    # Merge ATTOM data with mock data
                    self._merge_property_data(properties, attom_props)
            
            # Sort and filter results
            results = self._process_results(properties, filters)
            
            return {
                'success': True,
                'properties': results,
                'total': len(results),
                'data_sources': self._get_data_sources(results)
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {str(e)}")
            return {'error': 'Sorry, there was an error processing your query. Please try again.'}
    
    def _should_use_attom(self, filters: Dict) -> bool:
        """Determine if ATTOM API should be used based on filters"""
        # Check API usage
        usage = self.api_tracker.get_monthly_summary()
        if usage['reports_remaining'] <= 0:
            return False
        
        # Prioritize ATTOM for:
        # 1. Luxury properties (high price ranges)
        if filters.get('min_price', 0) > 1_000_000:
            return True
            
        # 2. Investment properties
        if filters.get('investment_property'):
            return True
            
        # 3. Specific property details needed
        if any(key in filters for key in ['foreclosure', 'include_financials']):
            return True
            
        # 4. New listings
        if filters.get('max_days_on_market', 100) < 7:
            return True
        
        return False
    
    def _merge_property_data(self, mock_props: List[Dict], attom_props: List[Dict]):
        """Merge ATTOM data into mock property data"""
        for attom_prop in attom_props:
            # Find matching mock property by location/features
            for mock_prop in mock_props:
                if self._properties_match(mock_prop, attom_prop):
                    # Enrich mock data with ATTOM details
                    mock_prop.update({
                        'last_sale_date': attom_prop.get('last_sale_date'),
                        'last_sale_price': attom_prop.get('last_sale_price'),
                        'owner_occupied': attom_prop.get('owner_occupied'),
                        'foreclosure_status': attom_prop.get('foreclosure_status'),
                        'data_source': 'hybrid'
                    })
                    break
    
    def _properties_match(self, prop1: Dict, prop2: Dict) -> bool:
        """Check if two properties likely represent the same property"""
        # For MVP, use simple matching based on ZIP and basic features
        return (
            prop1['zip_code'] == prop2['zip_code'] and
            abs(prop1['price'] - prop2.get('price', 0)) < 50000 and
            prop1.get('beds') == prop2.get('beds', prop1.get('beds'))
        )
    
    def _process_results(self, properties: List[Dict], filters: Dict) -> List[Dict]:
        """Process and sort property results"""
        # Apply any remaining filters
        results = []
        for prop in properties:
            if self._matches_filters(prop, filters):
                results.append(prop)
        
        # Sort results
        if filters.get('investment_property'):
            # Sort by potential ROI (simplified for MVP)
            results.sort(key=lambda x: x.get('price', 0))
        else:
            # Default sort by price
            results.sort(key=lambda x: x.get('price', float('inf')))
        
        return results
    
    def _matches_filters(self, prop: Dict, filters: Dict) -> bool:
        """Check if property matches all filters"""
        # Price filters
        if filters.get('min_price') and prop.get('price', 0) < filters['min_price']:
            return False
        if filters.get('max_price') and prop.get('price', 0) > filters['max_price']:
            return False
        
        # Bedroom filter
        if filters.get('min_beds') and prop.get('beds', 0) < filters['min_beds']:
            return False
        
        # Property type filter
        if filters.get('property_type') and prop.get('property_type') != filters['property_type']:
            return False
        
        # Days on market filter
        if filters.get('max_days_on_market'):
            if prop.get('days_on_market', 100) > filters['max_days_on_market']:
                return False
        
        # Price reduction filter
        if filters.get('only_reduced') and not prop.get('price_reduced'):
            return False
        
        return True
    
    def _get_data_sources(self, properties: List[Dict]) -> Dict:
        """Get summary of data sources used"""
        sources = {
            'redfin_mock': 0,
            'attom': 0,
            'hybrid': 0
        }
        
        for prop in properties:
            source = prop.get('data_source', 'redfin_mock')
            sources[source] += 1
        
        return sources

async def main():
    bot = RealEstateBot()
    
    # Example queries to show capabilities
    example_queries = [
        "Show me houses under $500k",
        "Find properties with at least 3 bedrooms",
        "Look for houses with price reductions",
        "Search for investment properties in 37215",
        "Find large houses over 3000 square feet",
        "Show me new listings in Belle Meade",
        "Find foreclosures under $600k",
        "Show me properties with high ROI potential"
    ]
    
    print("\nWelcome to Real Estate Search Bot!")
    print("Using hybrid approach:")
    print("- Primary: Redfin data for all properties")
    print("- Enhanced: ATTOM data for high-priority properties")
    print("\nYou can ask questions like:")
    for i, q in enumerate(example_queries, 1):
        print(f"{i}. {q}")
    
    while True:
        try:
            print("\nEnter your property search query (or 'quit' to exit):")
            query = input("> ").strip()
            
            if query.lower() in ('quit', 'exit', 'q'):
                break
            
            if query:
                result = await bot.search_properties(query)
                if 'error' in result:
                    print(result['error'])
                else:
                    print("\nSearch Results:")
                    for prop in result['properties']:
                        print(f"Address: {prop['address']}")
                        print(f"Price: ${prop['price']}")
                        print(f"Bedrooms: {prop['beds']}")
                        print(f"Bathrooms: {prop['baths']}")
                        print(f"Square Feet: {prop['square_feet']}")
                        print(f"Days on Market: {prop['days_on_market']}")
                        print(f"Price Reduced: {prop['price_reduced']}")
                        print(f"Data Source: {prop['data_source']}")
                        print()
                    print(f"Total Results: {result['total']}")
                    print(f"Data Sources: {result['data_sources']}")
                
        except EOFError:
            print("\nInput stream closed. Exiting...")
            break
        except KeyboardInterrupt:
            print("\nSearch cancelled.")
            break
        except Exception as e:
            logger.error(f"Error in main loop: {str(e)}")
            print("\nAn error occurred. Please try again.")
    
    print("\nThank you for using Real Estate Search Bot!")

if __name__ == "__main__":
    # Ensure data directory exists
    import os
    os.makedirs('data/cache', exist_ok=True)
    
    # Run the event loop
    import sys
    import asyncio
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    asyncio.run(main())
