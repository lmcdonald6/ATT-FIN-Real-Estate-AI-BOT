#!/usr/bin/env python3
"""
Street-Level Sentiment Analyzer

This module provides functionality to analyze sentiment for specific streets
within a ZIP code, using platform-specific scrapers and the Manus Agent Router.
"""

import json
import logging
import os
import sys
from typing import Dict, List, Any, Optional, Tuple

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import our components
from src.utils.zip_to_metro_mapping import get_metro_for_zip, get_data_sources_for_zip
from src.advanced.agent_router import ManusAgentRouter

# Import data collection and analysis components
try:
    from src.data_collection.social_scraper import get_posts_for_location
    from src.analysis.sentiment_analyzer import analyze_post_sentiment
    from src.data_management.neighborhood_cache import update_cache
except ImportError:
    logger.warning("Could not import all required modules. Using mock implementations.")
    
    # Mock implementations if the real ones are not available
    def get_posts_for_location(query: str, platform: str) -> List[Dict[str, Any]]:
        """Mock implementation of get_posts_for_location."""
        logger.info(f"Mock: Getting posts for {query} from {platform}")
        return [
            {"id": "1", "title": f"About {query}", "content": f"This area is pretty nice. {platform} has good reviews.", "date": "2025-05-01"},
            {"id": "2", "title": f"Living on {query.split(',')[0]}", "content": "The street is quiet and well-maintained.", "date": "2025-04-15"},
            {"id": "3", "title": f"Review of {query}", "content": "Good location, but traffic can be an issue during rush hour.", "date": "2025-03-22"},
        ]
    
    def analyze_post_sentiment(posts: List[Dict[str, Any]]) -> Tuple[str, float]:
        """Mock implementation of analyze_post_sentiment."""
        logger.info(f"Mock: Analyzing sentiment for {len(posts)} posts")
        content = " ".join([post.get("content", "") for post in posts])
        
        # Simple mock sentiment analysis
        positive_words = ["good", "nice", "well", "great", "excellent"]
        negative_words = ["bad", "issue", "problem", "terrible", "poor"]
        
        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())
        
        total = positive_count + negative_count
        if total == 0:
            score = 0.5
        else:
            score = positive_count / total
        
        if score > 0.7:
            summary = "Overall positive sentiment with good reviews."
        elif score > 0.4:
            summary = "Mixed sentiment with both positive and negative aspects."
        else:
            summary = "Generally negative sentiment with some concerns."
        
        return summary, score
    
    def update_cache(cache_key: str, posts: List[Dict[str, Any]], summary: str, score: float) -> None:
        """Mock implementation of update_cache."""
        logger.info(f"Mock: Updating cache for {cache_key} with score {score}")


def analyze_street_sentiment(street_name: str, zip_code: str, platform: str = None) -> Dict[str, Any]:
    """
    Analyze sentiment for a specific street within a ZIP code.
    Uses Manus platform-specific scrapers (Reddit, Yelp, TikTok, etc.)
    
    Args:
        street_name: Name of the street to analyze
        zip_code: ZIP code containing the street
        platform: Specific platform to use (if None, will use metro-based recommendation)
        
    Returns:
        Dictionary with analysis results
    """
    # Get metro information and recommended platforms
    metro = get_metro_for_zip(zip_code)
    recommended_platforms = get_data_sources_for_zip(zip_code)
    
    # Use the first recommended platform if none specified
    if not platform:
        platform = recommended_platforms[0] if recommended_platforms else "Reddit"
    
    query = f"{street_name}, {zip_code}"
    logger.info(f"Analyzing sentiment for {query} via {platform}")
    print(f"\nud83dudccd Crawling sentiment for {query} via {platform}...")
    
    # Get posts from the specified platform
    raw_posts = get_posts_for_location(query, platform)
    if not raw_posts:
        logger.warning(f"No posts found for {query} on {platform}")
        return {
            "status": "No posts found",
            "query": query,
            "street": street_name,
            "zip": zip_code,
            "metro": metro,
            "platform": platform,
            "recommended_platforms": recommended_platforms
        }
    
    # Analyze sentiment
    summary, score = analyze_post_sentiment(raw_posts)
    
    # Update cache
    cache_key = f"{zip_code}-{street_name.replace(' ', '_').lower()}"
    update_cache(cache_key, raw_posts, summary, score)
    
    logger.info(f"Completed sentiment analysis for {query}, score: {score}")
    
    return {
        "status": "Complete",
        "street": street_name,
        "zip": zip_code,
        "metro": metro,
        "platform": platform,
        "recommended_platforms": recommended_platforms,
        "score": score,
        "summary": summary,
        "posts": raw_posts[:3]  # preview of first 3 posts
    }


def analyze_multiple_streets(streets: List[str], zip_code: str) -> Dict[str, Any]:
    """
    Analyze sentiment for multiple streets within the same ZIP code.
    
    Args:
        streets: List of street names to analyze
        zip_code: ZIP code containing the streets
        
    Returns:
        Dictionary with analysis results for each street
    """
    # Get metro information and recommended platforms
    metro = get_metro_for_zip(zip_code)
    recommended_platforms = get_data_sources_for_zip(zip_code)
    
    # Use different platforms for different streets if multiple are recommended
    platforms_cycle = recommended_platforms if recommended_platforms else ["Reddit"]
    
    results = {}
    for i, street in enumerate(streets):
        # Cycle through recommended platforms
        platform = platforms_cycle[i % len(platforms_cycle)]
        
        # Analyze sentiment for this street
        result = analyze_street_sentiment(street, zip_code, platform)
        results[street] = result
    
    # Calculate average score
    valid_scores = [r["score"] for r in results.values() if r["status"] == "Complete"]
    avg_score = sum(valid_scores) / len(valid_scores) if valid_scores else 0
    
    return {
        "zip": zip_code,
        "metro": metro,
        "street_count": len(streets),
        "success_count": len(valid_scores),
        "average_score": avg_score,
        "streets": results
    }


def analyze_streets_in_multiple_zips(street_zip_pairs: List[Tuple[str, str]]) -> Dict[str, Any]:
    """
    Analyze sentiment for multiple street-ZIP pairs.
    
    Args:
        street_zip_pairs: List of (street, zip_code) tuples
        
    Returns:
        Dictionary with analysis results grouped by ZIP code
    """
    results = {}
    zip_groups = {}
    
    # Group streets by ZIP code
    for street, zip_code in street_zip_pairs:
        if zip_code not in zip_groups:
            zip_groups[zip_code] = []
        zip_groups[zip_code].append(street)
    
    # Analyze each ZIP code group
    for zip_code, streets in zip_groups.items():
        results[zip_code] = analyze_multiple_streets(streets, zip_code)
    
    # Calculate overall statistics
    all_scores = []
    for zip_results in results.values():
        valid_scores = [r["score"] for r in zip_results["streets"].values() if r["status"] == "Complete"]
        all_scores.extend(valid_scores)
    
    overall_avg = sum(all_scores) / len(all_scores) if all_scores else 0
    
    return {
        "zip_count": len(zip_groups),
        "street_count": len(street_zip_pairs),
        "success_count": len(all_scores),
        "overall_average_score": overall_avg,
        "results_by_zip": results
    }


if __name__ == "__main__":
    # Example usage
    print("\nud83cudfd9ufe0f Street-Level Sentiment Analysis")
    print("=" * 50)
    
    # Analyze a single street
    result = analyze_street_sentiment("Edgewood Ave", "30318", platform="Reddit")
    print("\nud83dudcca Single Street Analysis Result:")
    print(json.dumps(result, indent=2))
    
    # Analyze multiple streets in the same ZIP code
    streets = ["Edgewood Ave", "Peachtree St", "Ponce de Leon Ave"]
    multi_result = analyze_multiple_streets(streets, "30318")
    print("\nud83dudcca Multiple Streets Analysis:")
    print(f"ZIP: {multi_result['zip']} (Metro: {multi_result['metro']})")
    print(f"Streets analyzed: {multi_result['street_count']}")
    print(f"Average score: {multi_result['average_score']:.2f}")
    
    # Analyze streets across multiple ZIP codes
    street_zip_pairs = [
        ("Edgewood Ave", "30318"),  # Atlanta
        ("Bedford Ave", "11238"),   # NYC
        ("Valencia St", "94110")    # SF
    ]
    multi_zip_result = analyze_streets_in_multiple_zips(street_zip_pairs)
    print("\nud83dudcca Multi-ZIP Analysis:")
    print(f"ZIPs analyzed: {multi_zip_result['zip_count']}")
    print(f"Streets analyzed: {multi_zip_result['street_count']}")
    print(f"Overall average score: {multi_zip_result['overall_average_score']:.2f}")
