from typing import Dict
import aiohttp
from ..utils.cache import cache_result

@cache_result(ttl=86400)  # Cache for 24 hours
async def get_transit_score(zipcode: str) -> Dict[str, float]:
    """
    Analyze public transit accessibility and transportation infrastructure.
    
    Args:
        zipcode: The target zipcode to analyze
        
    Returns:
        Dict containing:
        - transit_score: Overall transit score (0-100)
        - public_transit_stops: Number of transit stops
        - bus_lines: Number of bus lines
        - rail_lines: Number of rail lines
        - avg_commute_time: Average commute time in minutes
    """
    try:
        async with aiohttp.ClientSession() as session:
            # TODO: Replace with actual API endpoint
            async with session.get(f"https://api.transit.example/{zipcode}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "transit_score": calculate_transit_score(data),
                        "public_transit_stops": data.get("transit_stops", 0),
                        "bus_lines": data.get("bus_lines", 0),
                        "rail_lines": data.get("rail_lines", 0),
                        "avg_commute_time": data.get("avg_commute", 0)
                    }
    except Exception as e:
        # Return default fallback data if API fails
        return {
            "transit_score": 50.0,  # Neutral score
            "public_transit_stops": 10,
            "bus_lines": 2,
            "rail_lines": 0,
            "avg_commute_time": 27.6,  # National average
            "error": str(e)
        }

def calculate_transit_score(data: Dict) -> float:
    """Calculate weighted transit score based on transportation metrics."""
    weights = {
        "transit_stops": 0.3,
        "bus_coverage": 0.2,
        "rail_coverage": 0.3,
        "commute_time": 0.2
    }
    
    # Normalize metrics
    stops_score = min(data.get("transit_stops", 0) / 50, 1.0)
    bus_score = min(data.get("bus_lines", 0) / 10, 1.0)
    rail_score = min(data.get("rail_lines", 0) / 3, 1.0)
    
    # Commute time score (lower is better)
    avg_commute = data.get("avg_commute", 30)
    commute_score = max(0, 1 - (avg_commute - 15) / 45)  # 15 min = perfect, 60 min = 0
    
    score = (
        stops_score * weights["transit_stops"] +
        bus_score * weights["bus_coverage"] +
        rail_score * weights["rail_coverage"] +
        commute_score * weights["commute_time"]
    ) * 100
    
    return round(min(score, 100), 2)
