"""Test nationwide property data generation"""
import asyncio
import os
from real_estate_bot import RealEstateBot

async def test_locations():
    # Create data directories (for caching)
    os.makedirs('data/cache', exist_ok=True)
    os.makedirs('data/usage', exist_ok=True)
    
    bot = RealEstateBot()
    
    # Test queries for different locations and property types
    test_queries = [
        # Urban luxury
        "Show me luxury condos in Manhattan under 3M",
        
        # Urban mid-range
        "Find townhouses in downtown Austin under 800k",
        
        # Suburban
        "Show me houses in Silicon Valley with at least 4 beds",
        
        # Original Nashville data (keeping MVP area)
        "Find investment properties in Green Hills with price reductions",
        
        # Test different property types
        "Show me multi-family properties in Miami under 1.5M"
    ]
    
    print("\nTesting nationwide property data generation...")
    print("=" * 80)
    
    for query in test_queries:
        print(f"\nTesting query: {query}")
        result = await bot.process_query(query)
        print(result)
        print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_locations())
