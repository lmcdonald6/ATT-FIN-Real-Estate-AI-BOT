"""Simple test script for real estate bot"""
import asyncio
from real_estate_bot import RealEstateBot

async def test_queries():
    bot = RealEstateBot()
    
    # Test queries that showcase our hybrid approach
    test_queries = [
        "Show me houses in Belle Meade under 2M",  # Tests area recognition and price parsing
        "Find investment properties in Green Hills",  # Tests investment property detection
        "Show me new listings with price reductions",  # Tests multiple filters
        "Find large houses in Brentwood",  # Tests implicit square footage
        "Show me foreclosures under 600k"  # Tests foreclosure detection
    ]
    
    print("\nRunning test queries to verify bot functionality...")
    for query in test_queries:
        print(f"\nTesting query: {query}")
        result = await bot.process_query(query)
        print(result)
        print("-" * 80)

if __name__ == "__main__":
    asyncio.run(test_queries())
