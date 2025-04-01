"""
Real Estate AI Bot - Main Entry Point
Handles property analysis, lead scoring, and market insights with structured responses
"""
import asyncio
import logging
from datetime import datetime
from typing import Dict, Optional

from .controller import RealEstateController
from .utils.formatter import ResponseFormatter

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RealEstateBot:
    """Main bot class handling all real estate queries with structured responses"""
    
    def __init__(self):
        self.controller = RealEstateController()
        self.formatter = ResponseFormatter()
        
    async def analyze_property(self, address: str, zipcode: str) -> Dict:
        """
        Comprehensive property analysis including:
        - Property value and details
        - Tax assessment
        - Owner information
        - Occupancy status
        - Distress indicators
        - Investment metrics
        """
        try:
            return await self.controller.analyze_property(address, zipcode)
        except Exception as e:
            logger.error(f"Error in property analysis: {str(e)}")
            return self._format_error('property_analysis', str(e))
    
    async def get_market_insights(self, zipcode: str) -> Dict:
        """
        Market analysis including:
        - Price trends
        - Sales metrics
        - Market health indicators
        - Rental market analysis
        """
        try:
            return await self.controller.get_market_insights(zipcode)
        except Exception as e:
            logger.error(f"Error in market analysis: {str(e)}")
            return self._format_error('market_analysis', str(e))
    
    async def score_lead(self, address: str, zipcode: str) -> Dict:
        """
        Lead scoring including:
        - Financial distress score
        - Time pressure score
        - Property condition score
        - Market position score
        - Recommended actions
        """
        try:
            property_data = await self.controller.analyze_property(address, zipcode)
            return await self.controller.score_lead(property_data)
        except Exception as e:
            logger.error(f"Error in lead scoring: {str(e)}")
            return self._format_error('lead_scoring', str(e))
    
    async def analyze_investment(self, address: str, zipcode: str) -> Dict:
        """
        Investment analysis including:
        - ARV calculation
        - Repair estimates
        - Deal metrics (MAO, ROI)
        - Exit strategy analysis
        """
        try:
            property_data = await self.controller.analyze_property(address, zipcode)
            return await self.controller.get_investment_analysis(property_data)
        except Exception as e:
            logger.error(f"Error in investment analysis: {str(e)}")
            return self._format_error('investment_analysis', str(e))
    
    def get_usage_stats(self) -> Dict:
        """
        Get API usage statistics including:
        - Daily and monthly usage
        - Cost analysis
        - Success rates
        - Optimization metrics
        """
        try:
            return self.controller.get_usage_stats()
        except Exception as e:
            logger.error(f"Error getting usage stats: {str(e)}")
            return self._format_error('usage_stats', str(e))
    
    def _format_error(self, query_type: str, error_message: str) -> Dict:
        """Format error response"""
        return {
            'error': error_message,
            'query_type': query_type,
            'timestamp': datetime.now().isoformat()
        }

async def test_bot():
    """Test the bot with comprehensive property analysis"""
    bot = RealEstateBot()
    
    try:
        # Test property analysis
        print("\nTesting Property Analysis:")
        property_analysis = await bot.analyze_property(
            "123 Main St",
            "12345"
        )
        print(property_analysis)
        
        # Test market analysis
        print("\nTesting Market Analysis:")
        market_analysis = await bot.get_market_insights("12345")
        print(market_analysis)
        
        # Test lead scoring
        print("\nTesting Lead Scoring:")
        lead_score = await bot.score_lead(
            "123 Main St",
            "12345"
        )
        print(lead_score)
        
        # Test investment analysis
        print("\nTesting Investment Analysis:")
        investment_analysis = await bot.analyze_investment(
            "123 Main St",
            "12345"
        )
        print(investment_analysis)
        
        # Get usage stats
        print("\nGetting Usage Stats:")
        usage_stats = bot.get_usage_stats()
        print(usage_stats)
        
    except Exception as e:
        logger.error(f"Test error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(test_bot())
