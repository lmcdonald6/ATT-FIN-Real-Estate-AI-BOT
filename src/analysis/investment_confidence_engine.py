#!/usr/bin/env python3
"""
Investment Confidence Engine

This module calculates a composite investment confidence score based on
market, reputation, trend, and economic scores, with optional adjustments
for vacancy rates, crime rates, and building permits.
"""

import logging
from typing import Dict, Any, Optional, Union, List, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def calculate_investment_confidence(
    market_score: float,
    reputation_score: float,
    trend_score: float,
    econ_score: float,
    vacancy_penalty: float = 0.0,
    crime_penalty: float = 0.0,
    permit_bonus: float = 0.0
) -> float:
    """
    Calculates a composite investment confidence score (0–100).
    Optional external adjustments: vacancy_penalty, crime_penalty, and permit_bonus.
    
    Args:
        market_score: Market performance score (0-100)
        reputation_score: Neighborhood reputation score (0-100)
        trend_score: Market trend score (0-100)
        econ_score: Economic indicators score (0-100)
        vacancy_penalty: Penalty for high vacancy rates (0+)
        crime_penalty: Penalty for high crime rates (0+)
        permit_bonus: Bonus for active building permits (0+)
        
    Returns:
        Investment confidence score (0-100)
    """
    base_score = (
        0.4 * market_score +
        0.3 * reputation_score +
        0.2 * trend_score +
        0.1 * econ_score
    )
    adjusted_score = base_score - vacancy_penalty - crime_penalty + permit_bonus
    return max(0, min(100, round(adjusted_score, 2)))


def get_investment_rating(score: float) -> str:
    """
    Convert a numerical investment confidence score to a letter rating.
    
    Args:
        score: Investment confidence score (0-100)
        
    Returns:
        Letter rating (A+, A, B+, B, C+, C, D+, D, F)
    """
    if score >= 90:
        return "A+"
    elif score >= 80:
        return "A"
    elif score >= 75:
        return "B+"
    elif score >= 70:
        return "B"
    elif score >= 65:
        return "C+"
    elif score >= 60:
        return "C"
    elif score >= 55:
        return "D+"
    elif score >= 50:
        return "D"
    else:
        return "F"


def get_investment_recommendation(score: float) -> str:
    """
    Convert a numerical investment confidence score to a recommendation.
    
    Args:
        score: Investment confidence score (0-100)
        
    Returns:
        Investment recommendation
    """
    if score >= 80:
        return "Strong Buy"
    elif score >= 70:
        return "Buy"
    elif score >= 60:
        return "Hold"
    elif score >= 50:
        return "Neutral"
    else:
        return "Avoid"


def calculate_full_investment_profile(
    market_score: float,
    reputation_score: float,
    trend_score: float,
    econ_score: float,
    adjustments: Optional[Dict[str, float]] = None
) -> Dict[str, Any]:
    """
    Calculate a complete investment profile including score, rating, and recommendation.
    
    Args:
        market_score: Market performance score (0-100)
        reputation_score: Neighborhood reputation score (0-100)
        trend_score: Market trend score (0-100)
        econ_score: Economic indicators score (0-100)
        adjustments: Optional dictionary of score adjustments
        
    Returns:
        Dictionary with investment profile
    """
    # Set default adjustments if none provided
    if adjustments is None:
        adjustments = {}
    
    # Extract adjustments with defaults
    vacancy_penalty = adjustments.get("vacancy_penalty", 0.0)
    crime_penalty = adjustments.get("crime_penalty", 0.0)
    permit_bonus = adjustments.get("permit_bonus", 0.0)
    
    # Calculate confidence score
    confidence_score = calculate_investment_confidence(
        market_score, reputation_score, trend_score, econ_score,
        vacancy_penalty, crime_penalty, permit_bonus
    )
    
    # Get rating and recommendation
    rating = get_investment_rating(confidence_score)
    recommendation = get_investment_recommendation(confidence_score)
    
    # Calculate component weights
    weights = {
        "market_weight": 0.4,
        "reputation_weight": 0.3,
        "trend_weight": 0.2,
        "econ_weight": 0.1
    }
    
    # Calculate component contributions
    contributions = {
        "market_contribution": weights["market_weight"] * market_score,
        "reputation_contribution": weights["reputation_weight"] * reputation_score,
        "trend_contribution": weights["trend_weight"] * trend_score,
        "econ_contribution": weights["econ_weight"] * econ_score,
        "adjustment_contribution": permit_bonus - vacancy_penalty - crime_penalty
    }
    
    # Return full profile
    return {
        "confidence_score": confidence_score,
        "rating": rating,
        "recommendation": recommendation,
        "weights": weights,
        "contributions": contributions,
        "adjustments": {
            "vacancy_penalty": vacancy_penalty,
            "crime_penalty": crime_penalty,
            "permit_bonus": permit_bonus,
            "net_adjustment": permit_bonus - vacancy_penalty - crime_penalty
        }
    }


if __name__ == "__main__":
    # Example usage
    market_score = 75
    reputation_score = 65
    trend_score = 55
    econ_score = 80
    
    # Basic calculation
    score = calculate_investment_confidence(
        market_score, reputation_score, trend_score, econ_score,
        vacancy_penalty=5, crime_penalty=3, permit_bonus=2
    )
    print(f"\nud83dudcc8 Investment Confidence Score: {score}/100")
    
    # Full profile calculation
    profile = calculate_full_investment_profile(
        market_score, reputation_score, trend_score, econ_score,
        adjustments={
            "vacancy_penalty": 5,
            "crime_penalty": 3,
            "permit_bonus": 2
        }
    )
    
    print(f"\nud83dudcca Full Investment Profile:")
    print(f"Score: {profile['confidence_score']}/100")
    print(f"Rating: {profile['rating']}")
    print(f"Recommendation: {profile['recommendation']}")
    
    print("\nComponent Contributions:")
    for component, value in profile['contributions'].items():
        print(f"{component}: {value:.2f} points")
