"""Quick test of real estate bot MVP"""
import asyncio
import os
from real_estate_bot import RealEstateBot

async def main():
    # Create data directories
    os.makedirs('data/cache', exist_ok=True)
    os.makedirs('data/usage', exist_ok=True)
    
    bot = RealEstateBot()
    
    # Test query that should trigger both Redfin and ATTOM data
    query = "Find investment properties in Green Hills with price reductions"
    print(f"\nTesting query: {query}")
    result = await bot.process_query(query)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
