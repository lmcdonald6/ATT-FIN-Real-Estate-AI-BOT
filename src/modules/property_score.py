# 🏠 Property Investment Scoring Module

from typing import Dict
from .rent_value_calc import rent_value_score

def appreciation_score(mock_zip: str) -> dict:
    """Calculate appreciation score based on historical data"""
    mock_appreciation = {
        "60614": 0.055,  # Chicago - Lincoln Park: 5.5% annual
        "90011": 0.042,  # Los Angeles: 4.2% annual
        "30318": 0.063   # Atlanta: 6.3% annual
    }
    rate = mock_appreciation.get(mock_zip, 0.04)  # Default: 4%
    
    if rate >= 0.06:  # 6%+ is strong
        return {
            "score": 85,
            "note": "Strong appreciation",
            "rate": f"{rate*100:.1f}%"
        }
    elif rate >= 0.04:  # 4-6% is moderate
        return {
            "score": 65,
            "note": "Moderate appreciation",
            "rate": f"{rate*100:.1f}%"
        }
    else:  # <4% is low
        return {
            "score": 45,
            "note": "Low appreciation",
            "rate": f"{rate*100:.1f}%"
        }

def get_market_factors(zip_code: str) -> Dict[str, float]:
    """Get market-specific adjustment factors"""
    return MARKET_ADJUSTMENTS.get(zip_code, DEFAULT_ADJUSTMENTS)

def risk_adjustments(zip_code: str) -> dict:
    """Calculate risk adjustments based on multiple market factors"""
    # Market risk factors
    vacancy_rate = {"60614": 0.045, "90011": 0.092, "30318": 0.037}
    tax_burden = {"60614": 1.9, "90011": 1.2, "30318": 0.9}
    crime_index = {"60614": 12.3, "90011": 28.7, "30318": 19.5}  # per 1000 residents
    price_volatility = {"60614": 0.08, "90011": 0.12, "30318": 0.09}  # annual std dev

    # Get values with defaults
    vacancy = vacancy_rate.get(zip_code, 0.06)
    tax = tax_burden.get(zip_code, 1.0)
    crime = crime_index.get(zip_code, 20.0)
    volatility = price_volatility.get(zip_code, 0.10)

    # Calculate penalties
    vacancy_penalty = -10 if vacancy > 0.08 else 0
    tax_penalty = -5 if tax > 1.5 else 0
    crime_penalty = -8 if crime > 25 else (-4 if crime > 20 else 0)
    volatility_penalty = -7 if volatility > 0.11 else (-3 if volatility > 0.09 else 0)

    total_penalty = vacancy_penalty + tax_penalty + crime_penalty + volatility_penalty

    return {
        "vacancy_rate": f"{vacancy*100:.1f}%",
        "tax_burden": f"{tax:.1f}%",
        "crime_index": f"{crime:.1f}",
        "price_volatility": f"{volatility*100:.1f}%",
        "score_penalty": total_penalty,
        "details": {
            "high_vacancy": vacancy > 0.08,
            "high_tax": tax > 1.5,
            "high_crime": crime > 20,
            "high_volatility": volatility > 0.09
        }
    }

def combined_score(zip_code: str, rent: float, value: float) -> dict:
    """Calculate combined investment score with risk adjustments"""
    # Get base scores
    rent_data = rent_value_score(rent, value)
    appreciation_data = appreciation_score(zip_code)
    risk_data = risk_adjustments(zip_code)
    
    # Calculate weighted base score
    base_score = (rent_data["score"] * 0.5) + (appreciation_data["score"] * 0.5)
    
    # Apply risk adjustments
    final_score = max(0, min(100, base_score + risk_data["score_penalty"]))
    
    # Determine overall rating
    if final_score >= 80:
        rating = "Excellent investment potential"
    elif final_score >= 65:
        rating = "Good investment opportunity"
    elif final_score >= 50:
        rating = "Moderate investment potential"
    else:
        rating = "Limited investment potential"

    return {
        "zip": zip_code,
        "combined_score": final_score,
        "overall_rating": rating,
        "rent_analysis": rent_data,
        "appreciation_analysis": appreciation_data,
        "risk_analysis": risk_data
    }
