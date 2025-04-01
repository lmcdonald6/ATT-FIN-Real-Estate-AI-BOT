from real_estate_controller import RealEstateController
import asyncio
import logging
from typing import Dict

class RealEstateAIBot:
    """Main entry point for the Real Estate AI Bot"""
    
    def __init__(self):
        # Initialize controller
        self.controller = RealEstateController()
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        
    async def analyze_property(self, zip_code: str, preferences: Dict) -> Dict:
        """Analyze properties in a given ZIP code based on preferences"""
        try:
            # Log request
            logging.info(f"Analyzing properties in ZIP: {zip_code}")
            
            # Process request through controller
            response = await self.controller.handle_property_query({
                'type': 'market_analysis',
                'zip_code': zip_code,
                'preferences': preferences
            })
            
            return response
            
        except Exception as e:
            logging.error(f"Error analyzing properties: {str(e)}")
            return {
                'error': 'Failed to analyze properties',
                'details': str(e)
            }

# Example usage
if __name__ == "__main__":
    # Initialize the bot
    bot = RealEstateAIBot()
    
    # Example request
    preferences = {
        'property_type': 'SFR',
        'min_beds': 3,
        'max_price': 500000
    }
    
    # Run the bot
    async def main():
        response = await bot.analyze_property('37208', preferences)
        print("Response:", response)
    
    asyncio.run(main())
