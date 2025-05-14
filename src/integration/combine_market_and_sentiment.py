#!/usr/bin/env python3
"""
Combine Market Analysis and Sentiment Analysis

This module integrates market analysis data with neighborhood sentiment data
to provide a comprehensive view of investment opportunities.
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Dict, Any, List, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Import our components
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import sys
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import existing modules
try:
    from src.market_analysis import analyze_market
except ImportError:
    logger.warning("Could not import market_analysis module. Using mock implementation.")
    
    # Mock market analysis function if the real one is not available
    def analyze_market(zip_code: str, rent: float = None, value: float = None, income: float = None) -> Dict[str, Any]:
        """
        Mock market analysis function.
        
        Args:
            zip_code: The ZIP code to analyze
            rent: Monthly rent (optional)
            value: Property value (optional)
            income: Annual income (optional)
            
        Returns:
            Dictionary with market analysis results
        """
        # Generate mock data based on the ZIP code
        market_data = {
            "median_price": 350000 + (int(zip_code[:2]) * 10000),
            "price_growth_1yr": 0.05 + (int(zip_code[-2:]) % 10) * 0.01,
            "rental_yield": 0.04 + (int(zip_code[-1]) % 5) * 0.005,
            "days_on_market": 30 - (int(zip_code[-1]) % 10) * 2,
            "inventory_months": 3.5 - (int(zip_code[-2:]) % 10) * 0.2,
            "market_health": 70 + (int(zip_code[-2:]) % 30),
            "last_updated": datetime.now().isoformat()
        }
        
        # Add market scores
        market_data["final_score"] = 65 + (int(zip_code[-2:]) % 25)
        market_data["trend_score"] = 60 + (int(zip_code[-1]) % 30)
        market_data["economic_score"] = 70 + (int(zip_code[-2]) % 20)
        market_data["summary"] = f"ZIP {zip_code} shows {market_data['price_growth_1yr']:.1%} annual growth with {market_data['rental_yield']:.1%} rental yield."
        
        return market_data


# Import neighborhood analysis pipeline
try:
    from neighborhood_full_pipeline import run_neighborhood_analysis
except ImportError:
    logger.warning("Could not import neighborhood_full_pipeline module. Using direct component calls.")
    from src.advanced.agent_router import ManusAgentRouter, choose_agent_source
    from src.advanced.refresh_agent import SentimentRefreshAgent, refresh_sentiment_for_zip
    from src.advanced.reputation_index import NeighborhoodReputationIndex
    
    async def run_neighborhood_analysis(zip_code: str) -> Dict[str, Any]:
        """
        Executes the full neighborhood analysis loop.
        
        Args:
            zip_code: The ZIP code to analyze
            
        Returns:
            Dictionary with analysis results
        """
        print(f"\n🧭 Routing request → ZIP: {zip_code}")
        source = choose_agent_source(zip_code)
        print(f"📡 Routed to source: {source}")

        print(f"🔄 Checking freshness + refreshing if needed...")
        await refresh_sentiment_for_zip(zip_code)

        print(f"📊 Computing reputation score...")
        reputation_index = NeighborhoodReputationIndex()
        index_result = reputation_index.compute_reputation_index(zip_code)

        return {
            "zip": zip_code,
            "source": source,
            "score_report": index_result
        }


async def get_sentiment_data(zip_code: str, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Get sentiment data for a ZIP code, refreshing if needed.
    
    Args:
        zip_code: The ZIP code to get sentiment data for
        force_refresh: Whether to force a refresh of the data
        
    Returns:
        Dictionary with sentiment analysis results
    """
    # Use the existing neighborhood analysis pipeline
    sentiment_result = await run_neighborhood_analysis(zip_code)
    
    return {
        "source": sentiment_result.get("source", "unknown"),
        "refreshed": True,  # Assume refreshed by the pipeline
        "reputation": sentiment_result.get("score_report", {})
    }


async def combined_analysis(zip_code: str, force_refresh: bool = False, rent: float = None, value: float = None, income: float = None) -> Dict[str, Any]:
    """
    Perform a combined market and sentiment analysis for a ZIP code.
    
    Args:
        zip_code: The ZIP code to analyze
        force_refresh: Whether to force a refresh of sentiment data
        rent: Monthly rent (optional)
        value: Property value (optional)
        income: Annual income (optional)
        
    Returns:
        Dictionary with combined analysis results
    """
    logger.info(f"Starting combined analysis for ZIP {zip_code}")
    print(f"\n📍 Running combined analysis for ZIP: {zip_code}")
    
    # Get market data
    market_data = analyze_market(zip_code, rent=rent, value=value, income=income)
    
    # Get sentiment data
    sentiment_data = await get_sentiment_data(zip_code, force_refresh)
    
    # Combine the data
    combined_data = {
        "zip": zip_code,
        "analysis_date": datetime.now().isoformat(),
        "market_summary": market_data.get("summary", ""),
        "market_score": market_data.get("final_score", 0),
        "trend_score": market_data.get("trend_score", 0),
        "econ_score": market_data.get("economic_score", 0),
        "reputation_score": sentiment_data.get("reputation", {}).get("overall_score", 0) * 100,
        "buzz_source": sentiment_data.get("source", "unknown"),
        "buzz_summary": sentiment_data.get("reputation", {}).get("summary", "")
    }
    
    # Add detailed data for further processing
    combined_data["_market_data"] = market_data
    combined_data["_sentiment_data"] = sentiment_data
    
    # Calculate combined investment score (0-100)
    market_score = market_data.get("final_score", 50)
    sentiment_score = sentiment_data.get("reputation", {}).get("overall_score", 0.5) * 100
    confidence = sentiment_data.get("reputation", {}).get("confidence_score", 0.5)
    
    # Weight sentiment more heavily when confidence is high
    sentiment_weight = 0.3 + (confidence * 0.2)  # 0.3 to 0.5 based on confidence
    market_weight = 1.0 - sentiment_weight
    
    investment_score = (market_score * market_weight) + (sentiment_score * sentiment_weight)
    
    # Add investment rating
    rating = "A+" if investment_score >= 90 else \
             "A" if investment_score >= 80 else \
             "B+" if investment_score >= 75 else \
             "B" if investment_score >= 70 else \
             "C+" if investment_score >= 65 else \
             "C" if investment_score >= 60 else \
             "D+" if investment_score >= 55 else \
             "D" if investment_score >= 50 else "F"
    
    # Add investment recommendation
    if investment_score >= 80:
        recommendation = "Strong Buy"
    elif investment_score >= 70:
        recommendation = "Buy"
    elif investment_score >= 60:
        recommendation = "Hold"
    elif investment_score >= 50:
        recommendation = "Neutral"
    else:
        recommendation = "Avoid"
    
    combined_data["investment_score"] = investment_score
    combined_data["investment_rating"] = rating
    combined_data["recommendation"] = recommendation
    combined_data["market_weight"] = market_weight
    combined_data["sentiment_weight"] = sentiment_weight
    
    logger.info(f"Completed combined analysis for ZIP {zip_code}, score: {investment_score:.2f}, rating: {rating}")
    
    return combined_data


async def batch_analysis(zip_codes: List[str], force_refresh: bool = False) -> List[Dict[str, Any]]:
    """
    Perform combined analysis for multiple ZIP codes.
    
    Args:
        zip_codes: List of ZIP codes to analyze
        force_refresh: Whether to force a refresh of sentiment data
        
    Returns:
        List of combined analysis results
    """
    results = []
    for zip_code in zip_codes:
        result = await combined_analysis(zip_code, force_refresh)
        results.append(result)
    
    return results


def combine_analysis(zip_code: str, rent: float = None, value: float = None, income: float = None) -> Dict[str, Any]:
    """
    Synchronous wrapper for combined_analysis.
    Runs full market + neighborhood analysis for a given ZIP.
    
    Args:
        zip_code: The ZIP code to analyze
        rent: Monthly rent (optional)
        value: Property value (optional)
        income: Annual income (optional)
        
    Returns:
        Dictionary with scores, summaries, and risk indicators
    """
    # Run the async function in a new event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        result = loop.run_until_complete(combined_analysis(zip_code, rent=rent, value=value, income=income))
        return result
    finally:
        loop.close()


async def main():
    """
    Example usage of the combined analysis module.
    """
    # Example ZIP codes
    test_zips = ["30318", "11238", "94110"]
    
    print("\n🔍 Running Combined Market & Sentiment Analysis")
    
    for zip_code in test_zips:
        print(f"\n📊 Analyzing ZIP {zip_code}...")
        result = await combined_analysis(zip_code)
        
        # Print a summary
        print("\n✅ Combined Analysis Result:")
        for key, val in result.items():
            if not key.startswith('_'):  # Skip internal fields
                print(f"{key}: {val}")
    
    print("\n✅ Analysis complete!")


if __name__ == "__main__":
    asyncio.run(main())
