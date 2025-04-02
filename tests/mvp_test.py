"""Test MVP property data generation"""
import asyncio
import os
from real_estate_bot import RealEstateBot

async def test_mvp():
    # Create data directories (for caching)
    os.makedirs('data/cache', exist_ok=True)
    os.makedirs('data/usage', exist_ok=True)
    
    bot = RealEstateBot()
    
    # Test queries focused on Nashville MVP areas
    test_queries = [
        # Green Hills (37215)
        "Show me luxury homes in Green Hills under 2M",
        
        # Belle Meade (37205)
        "Find investment properties in Belle Meade with price reductions",
        
        # Brentwood (37027)
        "Show me new listings in Brentwood with at least 4 beds",
        
        # Test property types
        "Find townhouses in Green Hills under 800k",
        
        # Test special conditions
        "Show me foreclosures in Belle Meade"
    ]
    
    print("\nTesting MVP Property Data Generation")
    print("Using hybrid approach:")
    print("- Primary: Mock Redfin data")
    print("- Secondary: Selective ATTOM enrichment")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\nTesting query: {query}")
        result = await bot.process_query(query)
        print(result)
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_mvp())
