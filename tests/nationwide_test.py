"""Test nationwide property search functionality"""
import asyncio
from real_estate_bot import RealEstateBot

async def test_nationwide():
    """Run nationwide property search tests"""
    print("\nTesting Nationwide Property Search")
    print("Using hybrid approach with smart data enrichment:")
    print("1. Mock Redfin data: Provides baseline property data")
    print("2. ATTOM enrichment: Enhances high-priority properties")
    print("=" * 80)
    
    bot = RealEstateBot()
    
    # Test queries for different markets
    test_queries = [
        "Show me investment properties in Green Hills under 2M",
        "Find luxury condos in Manhattan over 2M",
        "Show me houses in Silicon Valley with at least 4 beds",
        "Find townhouses in Miami under 800k",
        "Show me new construction in Austin under 1M",
        "Find investment properties in Dallas with price reductions",
        "Show me multi-family properties in Houston under 2M",
        "Find duplexes in Orlando with good ROI potential"
    ]
    
    for query in test_queries:
        print(f"\nTesting: {query}")
        result = await bot.search_properties(query)
        
        if 'error' in result:
            print(result['error'])
        else:
            print("\nFound Properties:")
            for prop in result['properties'][:3]:  # Show top 3 matches
                print(f"\nAddress: {prop['address']}")
                print(f"Price: ${prop['price']:,.2f}")
                print(f"Type: {prop['property_type']}")
                print(f"Beds/Baths: {prop.get('beds', 'N/A')}/{prop.get('baths', 'N/A')}")
                print(f"Square Feet: {prop.get('square_feet', 'N/A'):,}")
                
                # Show special features
                features = []
                if prop.get('price_reduced'):
                    features.append("Price Reduced")
                if prop.get('days_on_market', 100) <= 7:
                    features.append("New Listing")
                if features:
                    print(f"Features: {', '.join(features)}")
                
                # Show ATTOM data if available
                if prop.get('data_source') in ['attom', 'hybrid']:
                    print("Additional Details:")
                    if prop.get('last_sale_date'):
                        print(f"Last Sale: {prop['last_sale_date']} for ${prop.get('last_sale_price', 0):,.2f}")
                    if prop.get('owner_occupied') is not None:
                        print(f"Owner Occupied: {'Yes' if prop['owner_occupied'] else 'No'}")
                    if prop.get('foreclosure_status'):
                        print(f"Foreclosure Status: {prop['foreclosure_status']}")
            
            # Show summary
            print(f"\nTotal Results: {result['total']}")
            print("Data Sources:")
            for source, count in result['data_sources'].items():
                if count > 0:
                    print(f"- {source}: {count} properties")
        
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_nationwide())
