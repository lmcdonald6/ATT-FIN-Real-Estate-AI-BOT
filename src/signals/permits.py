from typing import Dict, Optional
import aiohttp
from ..utils.cache import cache_result

@cache_result(ttl=3600)  # Cache for 1 hour
async def get_permit_score(zipcode: str) -> Dict[str, float]:
    """
    Analyze building permits in the area to gauge development activity.
    
    Args:
        zipcode: The target zipcode to analyze
        
    Returns:
        Dict containing:
        - permit_score: Overall score (0-100)
        - residential_permits: Number of new residential permits
        - commercial_permits: Number of new commercial permits
        - renovation_permits: Number of renovation permits
    """
    try:
        async with aiohttp.ClientSession() as session:
            # TODO: Replace with actual API endpoint
            async with session.get(f"https://api.permits.example/{zipcode}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "permit_score": calculate_permit_score(data),
                        "residential_permits": data.get("residential", 0),
                        "commercial_permits": data.get("commercial", 0),
                        "renovation_permits": data.get("renovation", 0)
                    }
    except Exception as e:
        # Return default fallback data if API fails
        return {
            "permit_score": 50.0,  # Neutral score
            "residential_permits": 0,
            "commercial_permits": 0,
            "renovation_permits": 0,
            "error": str(e)
        }

def calculate_permit_score(data: Dict) -> float:
    """Calculate weighted permit score based on permit types and volumes."""
    weights = {
        "residential": 0.4,
        "commercial": 0.4,
        "renovation": 0.2
    }
    
    residential = min(data.get("residential", 0) / 100, 1.0)
    commercial = min(data.get("commercial", 0) / 50, 1.0)
    renovation = min(data.get("renovation", 0) / 200, 1.0)
    
    score = (
        residential * weights["residential"] +
        commercial * weights["commercial"] +
        renovation * weights["renovation"]
    ) * 100
    
    return round(min(score, 100), 2)
