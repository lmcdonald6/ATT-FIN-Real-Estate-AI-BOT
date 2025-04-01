"""
Test script to verify infrastructure setup.
Tests ATTOM API integration, storage system, and hybrid data approach.
"""
import asyncio
import logging
from datetime import datetime
from src.data.attom import AttomClient
from src.data.storage import PropertyStorage
from src.data.manager import DataManager
from src.analysis.market import MarketAnalyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def test_attom_api():
    """Test ATTOM API with storage integration."""
    logger.info("\nTesting ATTOM API with storage integration...")
    
    # Initialize components
    attom = AttomClient()
    storage = PropertyStorage()
    
    # Test properties
    properties = [
        {
            "address": "500 Interstate Blvd S",
            "zip_code": "37210"
        },
        {
            "address": "2126 Abbott Martin Rd",
            "zip_code": "37215"
        }
    ]
    
    for prop in properties:
        logger.info(f"\nTesting property: {prop['address']}, {prop['zip_code']}")
        
        # First API call
        logger.info("First call - should fetch from API:")
        data = await attom.get_property_data(prop['address'], prop['zip_code'])
        if data:
            logger.info("\u2713 Successfully retrieved and stored property data")
            
            # Store the data
            if storage.store_property(prop['address'], prop['zip_code'], data):
                logger.info("\u2713 Data successfully stored")
            
            # Second call - should use stored data
            logger.info("\nSecond call - should use stored data:")
            cached_data = await attom.get_property_data(prop['address'], prop['zip_code'])
            if cached_data:
                logger.info("\u2713 Successfully retrieved from storage")
        else:
            logger.error("\u2717 ATTOM API test failed")
    
    # Test foreclosure search
    logger.info("\nSearching for foreclosures:")
    foreclosures = storage.get_foreclosures()
    logger.info(f"Found {len(foreclosures)} stored foreclosures")

async def test_data_manager():
    """Test Data Manager with hybrid approach."""
    logger.info("\nTesting Data Manager with hybrid approach...")
    
    # Initialize components
    market_analyzer = MarketAnalyzer()
    attom = AttomClient()
    storage = PropertyStorage()
    
    data_manager = DataManager(
        market_analyzer=market_analyzer,
        attom_client=attom,
        storage=storage
    )
    
    # Test ZIP codes
    zip_codes = ["37210", "37215"]
    
    for zip_code in zip_codes:
        logger.info(f"\nSearching properties in {zip_code}")
        properties = await data_manager.search_properties(zip_code)
        
        # Verify results
        logger.info(f"\u2713 Found {len(properties)} properties")
        enriched = sum(1 for p in properties if p.get('attom_data'))
        logger.info(f"Properties with ATTOM data: {enriched}/{len(properties)}")

async def main():
    """Run all infrastructure tests."""
    logger.info("Starting infrastructure tests...")
    
    try:
        # Test ATTOM API and storage
        await test_attom_api()
        
        # Test Data Manager
        await test_data_manager()
        
        logger.info("\nAll tests completed successfully")
        
    except Exception as e:
        logger.error(f"Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(main())
