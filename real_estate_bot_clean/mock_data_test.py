"""
Test script to demonstrate mock data generation for different markets.
"""
import asyncio
import json
from src.data.manager import DataManager
from src.analysis.market import MarketAnalyzer
from src.data.attom import AttomClient
from src.data.storage import PropertyStorage

async def test_mock_data():
    # Initialize components
    market_analyzer = MarketAnalyzer()
    attom = AttomClient()
    storage = PropertyStorage()
    
    data_manager = DataManager(
        market_analyzer=market_analyzer,
        attom_client=attom,
        storage=storage
    )
    
    # Test different market types
    zip_codes = {
        "Luxury": "37215",  # Belle Meade/Green Hills
        "Urban": "37203",   # Downtown/Midtown
        "Suburban": "37211", # South Nashville
        "Up-and-Coming": "37208"  # North Nashville
    }
    
    print("\nMock Property Data Examples:")
    print("=" * 50)
    
    for market_type, zip_code in zip_codes.items():
        print(f"\n{market_type} Market (ZIP: {zip_code})")
        print("-" * 50)
        
        # Get properties
        properties = await data_manager.search_properties(zip_code)
        
        # Show 2 sample properties
        for i, prop in enumerate(properties[:2], 1):
            print(f"\nProperty {i}:")
            print(f"Address: {prop['address']}")
            print(f"Price: ${prop['price']:,}")
            print(f"Type: {prop['property_type']}")
            print(f"Specs: {prop['bedrooms']}bd/{prop['bathrooms']}ba, {prop['sqft']}sqft")
            print(f"Year Built: {prop['year_built']}")
            print(f"Status: {prop['status']}")
            print(f"Days on Market: {prop['days_on_market']}")

if __name__ == "__main__":
    asyncio.run(test_mock_data())
