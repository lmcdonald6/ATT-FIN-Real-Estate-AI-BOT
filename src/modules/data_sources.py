from .zoning_permit import get_zoning_data, get_permit_activity

# Property data functions
async def get_property_data(zip_code: str) -> dict:
    return {
        "median_price": 450000,
        "price_per_sqft": 275,
        "inventory_count": 45
    }

# Crime score (0-100, higher is safer)
async def get_crime_score(zip_code: str) -> float:
    scores = {
        "60614": 82.5,
        "90011": 65.0,
        "30318": 71.2
    }
    return scores.get(zip_code, 70.0)

# Market analysis functions
from .rent_value_calc import rent_value_score

async def get_rent_vs_value_score(zip_code: str) -> dict:
    """Calculate rent to value ratio score and analysis"""
    # Mock rental data
    rental_data = {
        "60614": {"rent": 2800, "value": 450000},  # 7.5% yield
        "90011": {"rent": 2200, "value": 380000},  # 7.0% yield
        "30318": {"rent": 2500, "value": 350000}   # 8.6% yield
    }
    
    data = rental_data.get(zip_code, {"rent": 2000, "value": 300000})
    return rent_value_score(data["rent"], data["value"])

async def get_market_trend_score(zip_code: str) -> float:
    """Analyze market trends and growth potential (0-100)"""
    scores = {
        "60614": 78.5,  # Steady growth
        "90011": 92.0,  # High growth potential
        "30318": 85.5   # Strong appreciation
    }
    return scores.get(zip_code, 80.0)
