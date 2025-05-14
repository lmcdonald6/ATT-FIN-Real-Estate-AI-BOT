#!/usr/bin/env python3
"""
Metro-Aware Investment Analyzer

This module integrates the investment confidence engine with the ZIP to metro mapping
and Manus Agent Router to create a location-aware investment analysis system.
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import our components
from src.integration.combine_market_and_sentiment import combine_analysis
from src.analysis.investment_confidence_engine import calculate_full_investment_profile
from src.utils.zip_to_metro_mapping import get_metro_for_zip, get_data_sources_for_zip
from src.advanced.agent_router import ManusAgentRouter


def analyze_zip_with_metro_awareness(zip_code: str, include_adjustments: bool = True) -> Dict[str, Any]:
    """
    Analyze a ZIP code with metro-aware adjustments and data source selection.
    
    Args:
        zip_code: The ZIP code to analyze
        include_adjustments: Whether to include metro-specific adjustments
        
    Returns:
        Dictionary with comprehensive analysis results
    """
    # Get metro information for the ZIP code
    metro = get_metro_for_zip(zip_code)
    
    # Configure the Manus Agent Router with metro-specific sources
    router = ManusAgentRouter()
    recommended_sources = get_data_sources_for_zip(zip_code)
    
    logger.info(f"Analyzing ZIP {zip_code} in metro area {metro or 'unknown'}")
    logger.info(f"Recommended data sources: {', '.join(recommended_sources)}")
    
    # Get base analysis from the combined market and sentiment analyzer
    base_analysis = combine_analysis(zip_code)
    
    # Apply metro-specific adjustments
    adjustments = {}
    
    if include_adjustments and metro:
        # These are example adjustments - customize based on real data
        metro_adjustments = {
            "nyc": {"vacancy_penalty": 2.0, "crime_penalty": 3.0, "permit_bonus": 5.0},
            "la": {"vacancy_penalty": 1.5, "crime_penalty": 2.5, "permit_bonus": 3.0},
            "chicago": {"vacancy_penalty": 3.0, "crime_penalty": 4.0, "permit_bonus": 2.0},
            "atlanta": {"vacancy_penalty": 1.0, "crime_penalty": 2.0, "permit_bonus": 4.0},
            "sf": {"vacancy_penalty": 1.0, "crime_penalty": 2.0, "permit_bonus": 6.0},
            "miami": {"vacancy_penalty": 2.0, "crime_penalty": 1.5, "permit_bonus": 3.0},
            "dallas": {"vacancy_penalty": 1.0, "crime_penalty": 1.0, "permit_bonus": 4.0}
        }
        
        adjustments = metro_adjustments.get(metro, {})
        logger.info(f"Applied metro-specific adjustments for {metro}: {adjustments}")
    
    # Calculate the investment confidence profile
    investment_profile = calculate_full_investment_profile(
        market_score=base_analysis.get("market_score", 0),
        reputation_score=base_analysis.get("reputation_score", 0),
        trend_score=base_analysis.get("trend_score", 0),
        econ_score=base_analysis.get("econ_score", 0),
        adjustments=adjustments
    )
    
    # Combine all results
    result = {
        **base_analysis,  # Include all base analysis data
        "metro": metro,
        "recommended_sources": recommended_sources,
        "investment_profile": investment_profile,
        "metro_adjustments": adjustments
    }
    
    return result


def generate_metro_investment_report(zip_codes: List[str]) -> Dict[str, Any]:
    """
    Generate a comprehensive investment report for multiple ZIP codes,
    grouped by metropolitan area.
    
    Args:
        zip_codes: List of ZIP codes to analyze
        
    Returns:
        Dictionary with analysis results grouped by metro
    """
    results = []
    metro_groups = {}
    
    # Analyze each ZIP code
    for zip_code in zip_codes:
        result = analyze_zip_with_metro_awareness(zip_code)
        results.append(result)
        
        # Group by metro
        metro = result.get("metro")
        if metro:
            if metro not in metro_groups:
                metro_groups[metro] = []
            metro_groups[metro].append(result)
    
    # Calculate metro averages
    metro_averages = {}
    for metro, metro_results in metro_groups.items():
        if not metro_results:
            continue
            
        # Calculate average scores
        avg_market_score = sum(r.get("market_score", 0) for r in metro_results) / len(metro_results)
        avg_reputation_score = sum(r.get("reputation_score", 0) for r in metro_results) / len(metro_results)
        avg_confidence_score = sum(r.get("investment_profile", {}).get("confidence_score", 0) for r in metro_results) / len(metro_results)
        
        # Store metro averages
        metro_averages[metro] = {
            "avg_market_score": avg_market_score,
            "avg_reputation_score": avg_reputation_score,
            "avg_confidence_score": avg_confidence_score,
            "zip_count": len(metro_results)
        }
    
    # Rank metros by average confidence score
    ranked_metros = sorted(
        [(metro, data["avg_confidence_score"]) for metro, data in metro_averages.items()],
        key=lambda x: x[1],
        reverse=True
    )
    
    return {
        "individual_results": results,
        "metro_groups": metro_groups,
        "metro_averages": metro_averages,
        "ranked_metros": ranked_metros
    }


if __name__ == "__main__":
    # Example ZIP codes across different metros
    test_zips = [
        "30318", "30319",  # Atlanta
        "11238", "11215",  # NYC
        "94110", "94103",  # SF
        "90210", "90001",  # LA
        "60614", "60601",  # Chicago
        "75201", "75202",  # Dallas
        "33101", "33109"   # Miami
    ]
    
    # Analyze a single ZIP code with metro awareness
    print("\nud83cudfd9ufe0f Metro-Aware Investment Analysis")
    print("=" * 50)
    
    zip_code = "30318"  # Atlanta
    print(f"\nud83dudccd Analyzing ZIP {zip_code}...")
    
    result = analyze_zip_with_metro_awareness(zip_code)
    
    print(f"\nZIP: {zip_code}")
    print(f"Metro: {result.get('metro', 'Unknown')}")
    print(f"Recommended Sources: {', '.join(result.get('recommended_sources', []))}")
    print(f"Market Score: {result.get('market_score', 0)}")
    print(f"Reputation Score: {result.get('reputation_score', 0)}")
    
    # Print investment profile
    profile = result.get("investment_profile", {})
    print(f"\nud83dudcb0 Investment Profile:")
    print(f"Confidence Score: {profile.get('confidence_score', 0)}/100")
    print(f"Rating: {profile.get('rating', 'N/A')}")
    print(f"Recommendation: {profile.get('recommendation', 'N/A')}")
    
    # Print adjustments
    adjustments = result.get("metro_adjustments", {})
    if adjustments:
        print(f"\nud83dudd27 Metro-Specific Adjustments:")
        for key, value in adjustments.items():
            print(f"{key}: {value}")
    
    # Generate a multi-ZIP report grouped by metro
    print("\n\nud83cudfe2 Metro Investment Report")
    print("=" * 50)
    
    report = generate_metro_investment_report(test_zips)
    
    # Print metro rankings
    print("\nud83cudfc6 Metro Rankings by Investment Confidence:")
    for i, (metro, score) in enumerate(report["ranked_metros"]):
        avg_data = report["metro_averages"][metro]
        print(f"{i+1}. {metro.upper()} - Score: {score:.1f}/100 - ZIPs: {avg_data['zip_count']}")
    
    # Print detailed metro averages
    print("\nud83dudcca Metro Averages:")
    for metro, data in report["metro_averages"].items():
        print(f"\n{metro.upper()}:")
        print(f"  Market Score: {data['avg_market_score']:.1f}")
        print(f"  Reputation Score: {data['avg_reputation_score']:.1f}")
        print(f"  Confidence Score: {data['avg_confidence_score']:.1f}")
        print(f"  ZIP Codes: {data['zip_count']}")
