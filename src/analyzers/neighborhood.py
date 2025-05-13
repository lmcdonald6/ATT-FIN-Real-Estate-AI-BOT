from typing import Dict, List
import asyncio
from ..signals import (
    get_permit_score,
    get_migration_score,
    get_crime_score,
    get_transit_score,
    get_zoning_score
)

async def analyze_neighborhood_potential(zipcode: str) -> Dict:
    """
    Analyze neighborhood potential by gathering and combining multiple signals.
    
    Args:
        zipcode: Target zipcode to analyze
        
    Returns:
        Dict containing:
        - overall_score: Combined neighborhood score (0-100)
        - signals: Individual signal scores and data
        - recommendations: List of key findings and recommendations
    """
    # Gather all signals concurrently
    signals = await asyncio.gather(
        get_permit_score(zipcode),
        get_migration_score(zipcode),
        get_crime_score(zipcode),
        get_transit_score(zipcode),
        get_zoning_score(zipcode)
    )
    
    # Unpack signals
    permit_data, migration_data, crime_data, transit_data, zoning_data = signals
    
    # Calculate overall score with weighted average
    weights = {
        "permits": 0.25,
        "demographics": 0.2,
        "crime": 0.2,
        "transit": 0.15,
        "zoning": 0.2
    }
    
    overall_score = round(sum([
        permit_data["permit_score"] * weights["permits"],
        migration_data["migration_score"] * weights["demographics"],
        crime_data["crime_score"] * weights["crime"],
        transit_data["transit_score"] * weights["transit"],
        zoning_data["zoning_score"] * weights["zoning"]
    ]), 2)
    
    # Generate recommendations based on signal data
    recommendations = generate_recommendations(
        permit_data,
        migration_data,
        crime_data,
        transit_data,
        zoning_data
    )
    
    return {
        "overall_score": overall_score,
        "signals": {
            "permits": permit_data,
            "demographics": migration_data,
            "crime": crime_data,
            "transit": transit_data,
            "zoning": zoning_data
        },
        "recommendations": recommendations
    }

def generate_recommendations(
    permit_data: Dict,
    migration_data: Dict,
    crime_data: Dict,
    transit_data: Dict,
    zoning_data: Dict
) -> List[str]:
    """Generate actionable recommendations based on signal data."""
    recommendations = []
    
    # Analyze permit trends
    if permit_data["permit_score"] > 70:
        recommendations.append(
            "Strong development activity indicates growth potential. "
            "Consider investing before property values increase further."
        )
    elif permit_data["permit_score"] < 30:
        recommendations.append(
            "Limited development activity. Look for off-market opportunities "
            "and potential for pioneering development."
        )
    
    # Analyze demographic trends
    if migration_data["population_growth"] > 2:
        recommendations.append(
            "Strong population growth suggests increasing demand. "
            "Focus on residential properties and rental units."
        )
    
    # Analyze crime trends
    if crime_data["crime_score"] < 40:
        recommendations.append(
            "Higher crime rates present risks. Consider security features "
            "and community improvement initiatives in investment strategy."
        )
    
    # Analyze transit accessibility
    if transit_data["transit_score"] > 70:
        recommendations.append(
            "Excellent transit access. Properties near transit stops "
            "may command premium rents."
        )
    
    # Analyze zoning potential
    if zoning_data["mixed_use"] > 20:
        recommendations.append(
            "High mixed-use zoning creates opportunities for diverse "
            "property types and development options."
        )
    
    return recommendations
