from typing import Dict
import aiohttp
from ..utils.cache import cache_result

@cache_result(ttl=86400)  # Cache for 24 hours
async def get_zoning_score(zipcode: str) -> Dict[str, float]:
    """
    Analyze zoning regulations and land use potential.
    
    Args:
        zipcode: The target zipcode to analyze
        
    Returns:
        Dict containing:
        - zoning_score: Overall zoning score (0-100)
        - mixed_use: Percentage of mixed-use zoning
        - development_potential: Development potential score
        - density_allowed: Maximum allowed density
        - zoning_changes: Recent or planned zoning changes
    """
    try:
        async with aiohttp.ClientSession() as session:
            # TODO: Replace with actual API endpoint
            async with session.get(f"https://api.zoning.example/{zipcode}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "zoning_score": calculate_zoning_score(data),
                        "mixed_use": data.get("mixed_use_pct", 0),
                        "development_potential": data.get("dev_potential", 0),
                        "density_allowed": data.get("max_density", 0),
                        "zoning_changes": data.get("recent_changes", [])
                    }
    except Exception as e:
        # Return default fallback data if API fails
        return {
            "zoning_score": 50.0,  # Neutral score
            "mixed_use": 15.0,     # 15% mixed-use
            "development_potential": 50.0,
            "density_allowed": 40,  # Units per acre
            "zoning_changes": [],
            "error": str(e)
        }

def calculate_zoning_score(data: Dict) -> float:
    """Calculate weighted zoning score based on land use factors."""
    weights = {
        "mixed_use": 0.3,
        "development_potential": 0.3,
        "density": 0.2,
        "zoning_changes": 0.2
    }
    
    # Normalize metrics
    mixed_use_score = min(data.get("mixed_use_pct", 0) / 30, 1.0)  # Cap at 30%
    dev_potential = min(data.get("dev_potential", 0) / 100, 1.0)
    density_score = min(data.get("max_density", 0) / 100, 1.0)  # Cap at 100 units/acre
    
    # Score recent zoning changes (more changes = more opportunity)
    changes = data.get("recent_changes", [])
    change_score = min(len(changes) / 5, 1.0)  # Cap at 5 changes
    
    score = (
        mixed_use_score * weights["mixed_use"] +
        dev_potential * weights["development_potential"] +
        density_score * weights["density"] +
        change_score * weights["zoning_changes"]
    ) * 100
    
    return round(min(score, 100), 2)
