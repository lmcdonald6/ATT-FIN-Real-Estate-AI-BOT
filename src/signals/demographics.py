from typing import Dict
import aiohttp
from ..utils.cache import cache_result

@cache_result(ttl=86400)  # Cache for 24 hours
async def get_migration_score(zipcode: str) -> Dict[str, float]:
    """
    Analyze demographic trends and migration patterns.
    
    Args:
        zipcode: The target zipcode to analyze
        
    Returns:
        Dict containing:
        - migration_score: Overall score (0-100)
        - population_growth: Annual population growth rate
        - median_income: Median household income
        - median_age: Median age of residents
        - employment_rate: Employment rate
    """
    try:
        async with aiohttp.ClientSession() as session:
            # TODO: Replace with actual API endpoint
            async with session.get(f"https://api.demographics.example/{zipcode}") as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return {
                        "migration_score": calculate_migration_score(data),
                        "population_growth": data.get("population_growth", 0),
                        "median_income": data.get("median_income", 0),
                        "median_age": data.get("median_age", 0),
                        "employment_rate": data.get("employment_rate", 0)
                    }
    except Exception as e:
        # Return default fallback data if API fails
        return {
            "migration_score": 50.0,  # Neutral score
            "population_growth": 1.0,  # 1% growth
            "median_income": 65000,    # National average
            "median_age": 38,          # National average
            "employment_rate": 0.94,    # National average
            "error": str(e)
        }

def calculate_migration_score(data: Dict) -> float:
    """Calculate weighted migration score based on demographic indicators."""
    weights = {
        "population_growth": 0.3,
        "income_growth": 0.3,
        "employment": 0.2,
        "age_diversity": 0.2
    }
    
    # Normalize each factor to 0-1 range
    pop_growth = min(max(data.get("population_growth", 0) / 5, 0), 1)  # Cap at 5% growth
    income_growth = min(max(data.get("income_growth", 0) / 10, 0), 1)  # Cap at 10% growth
    employment = min(data.get("employment_rate", 0), 1)
    age_diversity = calculate_age_diversity(data.get("age_distribution", {}))
    
    score = (
        pop_growth * weights["population_growth"] +
        income_growth * weights["income_growth"] +
        employment * weights["employment"] +
        age_diversity * weights["age_diversity"]
    ) * 100
    
    return round(min(score, 100), 2)

def calculate_age_diversity(age_dist: Dict) -> float:
    """Calculate age diversity score based on age distribution."""
    if not age_dist:
        return 0.5  # Default middle score
    
    # Ideal distribution percentages
    ideal = {
        "0-18": 0.23,
        "19-34": 0.25,
        "35-54": 0.27,
        "55+": 0.25
    }
    
    # Calculate deviation from ideal distribution
    total_deviation = sum(abs(age_dist.get(age, 0) - ideal_pct) 
                         for age, ideal_pct in ideal.items())
    
    # Convert to 0-1 score (lower deviation is better)
    return max(0, 1 - (total_deviation / 2))
