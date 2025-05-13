from typing import Dict
import aiohttp
from ..utils.cache import cache_result

@cache_result(ttl=43200)  # Cache for 12 hours
async def get_crime_score(zipcode: str) -> Dict[str, float]:
    """
    Analyze crime statistics and safety indicators.
    
    Args:
        zipcode: The target zipcode to analyze
        
    Returns:
        Dict containing:
        - crime_score: Overall safety score (0-100, higher is safer)
        - violent_crime_rate: Violent crimes per 100k residents
        - property_crime_rate: Property crimes per 100k residents
        - crime_trend: Year-over-year crime rate change
    """
    try:
        async with aiohttp.ClientSession() as session:
            # TODO: Replace with actual API endpoint
            async with session.get(f"https://api.crime.example/{zipcode}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "crime_score": calculate_crime_score(data),
                        "violent_crime_rate": data.get("violent_rate", 0),
                        "property_crime_rate": data.get("property_rate", 0),
                        "crime_trend": data.get("trend", 0)
                    }
    except Exception as e:
        # Return default fallback data if API fails
        return {
            "crime_score": 50.0,  # Neutral score
            "violent_crime_rate": 366.7,  # National average
            "property_crime_rate": 2109.9,  # National average
            "crime_trend": 0,  # Flat trend
            "error": str(e)
        }

def calculate_crime_score(data: Dict) -> float:
    """Calculate weighted crime score based on various crime statistics."""
    weights = {
        "violent_crime": 0.4,
        "property_crime": 0.3,
        "trend": 0.3
    }
    
    # Normalize crime rates (lower is better)
    # Using national averages as baseline
    violent_score = max(0, 1 - (data.get("violent_rate", 0) / 500))
    property_score = max(0, 1 - (data.get("property_rate", 0) / 2500))
    
    # Trend score (-10% or better = 1, +10% or worse = 0)
    trend = data.get("trend", 0)
    trend_score = max(0, min(1, (10 - trend) / 20))
    
    score = (
        violent_score * weights["violent_crime"] +
        property_score * weights["property_crime"] +
        trend_score * weights["trend"]
    ) * 100
    
    return round(min(score, 100), 2)
