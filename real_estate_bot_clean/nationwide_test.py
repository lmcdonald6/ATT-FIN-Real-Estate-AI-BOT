"""
Test nationwide property search functionality.
Tests multiple markets with mock data and selective ATTOM enrichment.
"""
import asyncio
from src.data.manager import DataManager

async def test_markets():
    """Test property search across different markets."""
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Test markets
    markets = {
        "Nashville Luxury": "37215",
        "Nashville Urban": "37203",
        "Atlanta Luxury": "30305",
        "Atlanta Urban": "30308",
        "Dallas Luxury": "75225",
        "Dallas Urban": "75201"
    }
    
    # Search each market
    for market_name, zip_code in markets.items():
        print(f"\nSearching {market_name} (ZIP: {zip_code})")
        print("-" * 50)
        
        # Get properties
        properties = await data_manager.search_properties(zip_code)
        
        if not properties:
            print(f"No properties found in {zip_code}")
            continue
        
        # Calculate market summary
        total_price = sum(float(p.get("price", 0)) for p in properties)
        total_sqft = sum(float(p.get("sqft", 0)) for p in properties)
        total_dom = sum(float(p.get("days_on_market", 0)) for p in properties)
        
        print(f"\nFound {len(properties)} properties\n")
        print("Market Summary:")
        print(f"Average Price: ${total_price/len(properties):,.2f}")
        print(f"Average Sqft: {int(total_sqft/len(properties)):,}")
        print(f"Average Days on Market: {total_dom/len(properties):.1f}\n")
        
        # Show sample properties
        print("Sample Properties:\n")
        for i, prop in enumerate(properties[:2], 1):
            print(f"Property {i}:")
            print(f"Address: {prop.get('address', 'N/A')}")
            print(f"Price: ${int(prop.get('price', 0)):,}")
            print(f"Type: {prop.get('property_type', 'N/A')}")
            print(f"Specs: {prop.get('bedrooms', 0)}bd/{prop.get('bathrooms', 0)}ba, {int(prop.get('sqft', 0))}sqft")
            print(f"Year Built: {prop.get('year_built', 'N/A')}")
            print(f"Status: {prop.get('status', 'N/A')}")
            print(f"Days on Market: {prop.get('days_on_market', 'N/A')}")
            print(f"Data Source: {prop.get('data_source', 'N/A')}\n")

if __name__ == "__main__":
    asyncio.run(test_markets())
