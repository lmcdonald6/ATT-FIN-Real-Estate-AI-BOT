"""
Test script for neighborhood sentiment analysis feature using mock data.
"""

import asyncio
import json
from src.utils.neighborhood_sentiment_mock import analyze_neighborhood_sentiment


async def test_sentiment_analysis():
    """
    Test the neighborhood sentiment analysis feature with different locations using mock data.
    """
    # List of neighborhoods to analyze
    neighborhoods = [
        "Atlanta Beltline",
        "Midtown Manhattan",
        "Mission District San Francisco",
        "Random Neighborhood"  # This will use generic mock data
    ]
    
    results = {}
    
    for neighborhood in neighborhoods:
        print(f"\nAnalyzing sentiment for: {neighborhood}")
        sentiment_data = await analyze_neighborhood_sentiment(neighborhood)
        results[neighborhood] = sentiment_data
        
        print(f"Data source: {sentiment_data['data_source']}")
        print(f"Posts analyzed: {sentiment_data['posts_analyzed']}")
        if sentiment_data['success']:
            print("Summary excerpt:")
            print(sentiment_data['sentiment_summary'][:200] + "...")
        else:
            print(f"Error: {sentiment_data['message']}")
    
    # Save results to file
    with open("neighborhood_sentiment_results_mock.json", "w") as f:
        json.dump(results, f, indent=2)
        print(f"\nResults saved to neighborhood_sentiment_results_mock.json")


if __name__ == "__main__":
    asyncio.run(test_sentiment_analysis())
