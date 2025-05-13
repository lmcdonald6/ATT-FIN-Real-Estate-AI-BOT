# 🏢 Zoning & Permit Mock Module

# Building department URLs
BUILDING_DEPT_URLS = {
    "60614": "https://www.chicago.gov/city/en/depts/bldgs.html",
    "90011": "https://www.lacity.org/government/departments/building-safety",
    "30318": "https://www.atlantaga.gov/government/departments/city-planning"
}

def get_building_dept_url(zip_code: str) -> str:
    """Get the building department URL for a given ZIP code"""
    return BUILDING_DEPT_URLS.get(zip_code, "")

async def get_zoning_data(zip_code: str) -> dict:

    # Mock zoning categories
    zoning_types = {
        "60614": "Residential R3",
        "90011": "Mixed Use MX2",
        "30318": "Industrial I1"
    }
    return {
        "zoning_type": zoning_types.get(zip_code, "Unknown"),
        "density_rating": "Medium",
        "recent_rezoning_activity": True
    }

async def get_permit_activity(zip_code: str) -> dict:
    """Get detailed permit activity for a ZIP code"""
    # Mock permit activity with detailed project data
    permit_data = {
        "60614": {  # Chicago - Lincoln Park
            "permits_issued": 12,
            "major_construction": 2,
            "active_projects": [
                {"type": "multi-family", "status": "approved", "units": 24},
                {"type": "ADU", "status": "pending", "units": 1},
                {"type": "mixed-use", "status": "in_review", "units": 8}
            ]
        },
        "90011": {  # Los Angeles
            "permits_issued": 5,
            "major_construction": 1,
            "active_projects": [
                {"type": "commercial", "status": "approved", "sqft": 15000},
                {"type": "ADU", "status": "approved", "units": 1}
            ]
        },
        "30318": {  # Atlanta
            "permits_issued": 20,
            "major_construction": 6,
            "active_projects": [
                {"type": "multi-family", "status": "under_construction", "units": 45},
                {"type": "townhomes", "status": "approved", "units": 12},
                {"type": "mixed-use", "status": "approved", "units": 30}
            ]
        }
    }
    
    # Default data for unknown ZIP codes
    return permit_data.get(zip_code, {
        "permits_issued": 0,
        "major_construction": 0,
        "active_projects": []
    })
