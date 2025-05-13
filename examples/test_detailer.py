import asyncio
import json
import os
from dotenv import load_dotenv
from src.agents.detailer import scrape_local_building_data

# Load environment variables
load_dotenv()

async def test_scraping():
    # Test different city URLs
    urls = [
        "https://www.chicago.gov/city/en/depts/bldgs/provdrs/permits.html",
        "https://planning.lacity.org/zoning",
        "https://www.atlantaga.gov/government/departments/city-planning"
    ]
    
    print("\nZoning & Permit Scraping Test")
    print("=" * 50)
    
    for url in urls:
        print(f"\nScraping {url}...")
        result = await scrape_local_building_data(url)
        
        if not result["success"]:
            print(f"Error: {result['error']}")
            continue
            
        analysis = result["analysis"]
        print("\nExtracted Information:")
        print("-" * 20)
        print(f"Zoning Type: {analysis['zoning_type']}")
        print(f"Recent Rezoning Activity: {analysis['rezoning_activity']}")
        print(f"Monthly Permit Volume: {analysis['permit_volume']}")
        
        if analysis['recent_applications']:
            print("\nRecent Applications:")
            for app in analysis['recent_applications']:
                print(f"- {app}")
                
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_scraping())
