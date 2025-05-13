"""Property scoring and analysis module."""

from typing import Dict, Tuple
import numpy as np

def calculate_investment_score(
    property_data: Dict,
    market_data: Dict,
    crime_data: Dict,
    census_data: Dict
) -> Tuple[int, Dict]:
    """Calculate investment score and risk factors."""
    
    # Weights for different factors
    weights = {
        "market_growth": 0.3,
        "crime_rate": 0.2,
        "demographics": 0.2,
        "property_metrics": 0.3
    }
    
    # Market Growth Score (0-100)
    market_score = min(100, max(0, float(market_data.get("price_growth_1y", 0)) * 10))
    
    # Crime Score (0-100, lower crime = higher score)
    crime_rate = crime_data.get("violent_crime_rate", 0) + crime_data.get("property_crime_rate", 0)
    crime_score = max(0, 100 - (crime_rate / 50))  # Normalize crime rate
    
    # Demographics Score
    income_score = min(100, census_data.get("median_income", 0) / 1000)
    employment_score = census_data.get("employment_rate", 0) * 100
    population_growth = census_data.get("population_growth", 0)
    demographics_score = (income_score + employment_score + (population_growth * 20)) / 3
    
    # Property Metrics
    cap_rate = float(market_data.get("cap_rate_avg", 0))
    vacancy_rate = float(market_data.get("rental_vacancy", 0))
    property_score = (cap_rate * 10) + (10 - vacancy_rate) * 5
    
    # Calculate final score
    final_score = (
        weights["market_growth"] * market_score +
        weights["crime_rate"] * crime_score +
        weights["demographics"] * demographics_score +
        weights["property_metrics"] * property_score
    )
    
    # Risk assessment
    risk_factors = []
    if market_score < 50:
        risk_factors.append("Low market growth potential")
    if crime_score < 60:
        risk_factors.append("High crime rate in area")
    if demographics_score < 50:
        risk_factors.append("Weak demographic indicators")
    if property_score < 50:
        risk_factors.append("Poor property metrics")
        
    risk_score = 100 - (len(risk_factors) * 25)
    
    return int(final_score), {
        "risk_score": risk_score,
        "risk_factors": risk_factors,
        "component_scores": {
            "market_growth": market_score,
            "crime": crime_score,
            "demographics": demographics_score,
            "property": property_score
        }
    }

def get_recommendation(score: int, risk_score: int) -> str:
    """Get investment recommendation based on scores."""
    if score >= 75 and risk_score >= 60:
        return "BUY"
    elif score >= 60 and risk_score >= 40:
        return "HOLD"
    else:
        return "SKIP"
