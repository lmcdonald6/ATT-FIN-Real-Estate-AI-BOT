#!/usr/bin/env python3
"""
Real Estate Intelligence Hub

This script integrates all components of the autonomous real estate analysis system:
1. Market analysis from analyze_market()
2. Neighborhood sentiment analysis from the autonomous backend
3. Airtable export for tracking and visualization
4. Leaderboard generation for top neighborhoods

This provides a complete decision-making interface for real estate investment analysis.
"""

import asyncio
import json
import logging
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.abspath(__file__))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import our components
from src.integration.combine_market_and_sentiment import combine_analysis
from src.utils.airtable_exporter import export_to_airtable
from src.integration.leaderboard_generator import LeaderboardGenerator


async def analyze_zip_codes(zip_codes: List[str], export_to_airtable: bool = True) -> List[Dict[str, Any]]:
    """
    Analyze a list of ZIP codes and optionally export results to Airtable.
    
    Args:
        zip_codes: List of ZIP codes to analyze
        export_to_airtable: Whether to export results to Airtable
        
    Returns:
        List of analysis results
    """
    results = []
    
    print(f"\n🚀 Starting analysis of {len(zip_codes)} ZIP codes...")
    
    for zip_code in zip_codes:
        print(f"\n📍 Analyzing ZIP {zip_code}...")
        
        # Use the combined analysis function
        result = combine_analysis(zip_code)
        results.append(result)
        
        # Print a summary of the results
        print("\n✅ Analysis complete!")
        print(f"Market Score: {result.get('market_score', 0)}/100")
        print(f"Reputation Score: {result.get('reputation_score', 0):.1f}/100")
        print(f"Investment Score: {result.get('investment_score', 0):.1f}/100 ({result.get('investment_rating', 'N/A')})")
        print(f"Recommendation: {result.get('recommendation', 'N/A')}")
        
        # Print summaries
        print(f"\nMarket Summary: {result.get('market_summary', 'No data')}")
        print(f"Neighborhood Buzz: {result.get('buzz_summary', 'No data')[:150]}...")
    
    # Export to Airtable if requested
    if export_to_airtable:
        try:
            from src.utils.airtable_exporter import export_to_airtable as airtable_export
            export_result = airtable_export(results)
            print(f"\n📊 Exported {export_result.get('success', 0)}/{export_result.get('total', 0)} results to Airtable")
        except Exception as e:
            logger.error(f"Error exporting to Airtable: {str(e)}")
            print(f"\n⚠️ Error exporting to Airtable: {str(e)}")
    
    return results


async def generate_leaderboards(results: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Generate leaderboards from analysis results.
    
    Args:
        results: List of analysis results
        
    Returns:
        Dictionary with paths to exported leaderboards
    """
    print("\n🏆 Generating leaderboards...")
    
    generator = LeaderboardGenerator()
    
    # Generate leaderboards for different metrics
    metrics = [
        ("investment", "Investment Score"),
        ("market", "Market Performance"),
        ("sentiment", "Neighborhood Reputation")
    ]
    
    exports = {}
    
    for metric_key, metric_name in metrics:
        print(f"\n📊 Generating {metric_name} Leaderboard...")
        
        # Map our metrics to the leaderboard generator's metrics
        if metric_key == "investment":
            sort_key = lambda x: x.get("investment_score", 0)
        elif metric_key == "market":
            sort_key = lambda x: x.get("market_score", 0)
        elif metric_key == "sentiment":
            sort_key = lambda x: x.get("reputation_score", 0)
        else:
            sort_key = lambda x: 0
        
        # Sort the results
        sorted_results = sorted(results, key=sort_key, reverse=True)
        
        # Format the leaderboard
        leaderboard = []
        for i, result in enumerate(sorted_results):
            entry = {
                "rank": i + 1,
                "zip_code": result.get("zip"),
                "investment_score": result.get("investment_score", 0),
                "investment_rating": result.get("investment_rating", "N/A"),
                "market_score": result.get("market_score", 0),
                "sentiment_score": result.get("reputation_score", 0),
                "median_price": result.get("_market_data", {}).get("median_price", 0),
                "price_growth": result.get("_market_data", {}).get("price_growth_1yr", 0),
                "rental_yield": result.get("_market_data", {}).get("rental_yield", 0),
                "recommendation": result.get("recommendation", "N/A")
            }
            leaderboard.append(entry)
            
            # Print the top entries
            if i < 5:
                print(f"{i+1}. ZIP {entry['zip_code']} - Score: {sort_key(result):.1f} - {entry['recommendation']}")
        
        # Export to CSV and HTML
        try:
            csv_path = generator.export_leaderboard_to_csv(leaderboard, metric=metric_key)
            html_path = generator.export_html_report(leaderboard, 
                                                  title=f"Top Neighborhoods by {metric_name}",
                                                  metric=metric_key)
            
            exports[f"{metric_key}_csv"] = csv_path
            exports[f"{metric_key}_html"] = html_path
        except Exception as e:
            logger.error(f"Error exporting leaderboard: {str(e)}")
            print(f"⚠️ Error exporting leaderboard: {str(e)}")
    
    print("\n✅ Leaderboard generation complete!")
    return exports


async def run_intelligence_hub():
    """
    Run the complete real estate intelligence hub workflow.
    """
    print("\n🏘️ Real Estate Intelligence Hub")
    print("Powered by Autonomous Sentiment Analysis & Market Analytics")
    print("=" * 60)
    
    # Define ZIP codes to analyze
    # You can expand this list or load from a file
    zip_codes = [
        # Atlanta
        "30318", "30319", "30306", "30307", "30308", 
        # Brooklyn
        "11238", "11215", "11217", "11201", "11205",
        # San Francisco
        "94110", "94103", "94107", "94109", "94117"
    ]
    
    # Run analysis
    results = await analyze_zip_codes(zip_codes)
    
    # Generate leaderboards
    exports = await generate_leaderboards(results)
    
    # Print export paths
    print("\n📁 Exported Files:")
    for key, path in exports.items():
        print(f"{key}: {path}")
    
    print("\n🎉 Intelligence Hub processing complete!")
    print("You can now view the results in Airtable or open the HTML reports.")


def main():
    """
    Main entry point for the script.
    """
    # Create output directory if it doesn't exist
    output_dir = os.path.join(os.path.dirname(__file__), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Run the async main function
    asyncio.run(run_intelligence_hub())


if __name__ == "__main__":
    main()
