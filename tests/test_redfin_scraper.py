"""Test script for Redfin scraper"""
import sys
import os
import asyncio
from tools.redfin_scraper import search_properties

# Add tools directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), 'tools'))

async def main():
    # Test ZIP codes
    zip_codes = ['37215', '37205', '37027']  # Green Hills, Belle Meade, Brentwood
    print(f"\nSearching ZIP codes: {zip_codes}")
    
    # Test filters
    filters = {
        'max_price': 1500000,
        'min_beds': 4
    }
    
    # Search each ZIP code
    for zip_code in zip_codes:
        print(f"\nSearching {zip_code}...")
        properties = await search_properties(zip_code, filters.get('max_price'), filters.get('min_beds'))
        
        if properties:
            print(f"\nFound {len(properties)} properties in {zip_code}:")
            for prop in properties[:3]:  # Show first 3 as preview
                print(f"- {prop['address']}: ${prop['price']:,}")
            if len(properties) > 3:
                print(f"... and {len(properties) - 3} more properties")
        else:
            print(f"No properties found in {zip_code}")
            
        # Delay between searches
        if zip_code != zip_codes[-1]:
            delay = 30
            print(f"\nWaiting {delay} seconds before next search...")
            await asyncio.sleep(delay)

if __name__ == "__main__":
    asyncio.run(main())
