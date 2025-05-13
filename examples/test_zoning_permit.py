import asyncio
import sys
import os

# Add project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.modules.zoning_permit import get_zoning_data, get_permit_activity, get_building_dept_url

async def test_zoning_permit():
    print("\nZoning & Permit Data Test")
    print("=" * 50)
    
    for zip_code in ["60614", "90011", "30318", "99999"]:
        print(f"\nTesting ZIP: {zip_code}")
        print("-" * 20)
        
        # Get building department URL
        dept_url = get_building_dept_url(zip_code)
        if dept_url:
            print(f"Building Department: {dept_url}\n")
        
        zoning = await get_zoning_data(zip_code)
        permits = await get_permit_activity(zip_code)
        
        print("Zoning Data:")
        print(f"  Type: {zoning['zoning_type']}")
        print(f"  Density: {zoning['density_rating']}")
        print(f"  Recent Rezoning: {zoning['recent_rezoning_activity']}")
        
        print("\nPermit Activity:")
        print(f"  Permits Issued: {permits['permits_issued']}")
        print(f"  Major Construction: {permits['major_construction']}")
        
        if permits['active_projects']:
            print("\nActive Projects:")
            for project in permits['active_projects']:
                print(f"  - {project['type'].title()}:")
                print(f"    Status: {project['status'].replace('_', ' ').title()}")
                if 'units' in project:
                    print(f"    Units: {project['units']}")
                if 'sqft' in project:
                    print(f"    Square Feet: {project['sqft']:,}")
        
        print("-" * 50)

if __name__ == "__main__":
    asyncio.run(test_zoning_permit())
