#!/usr/bin/env python3
"""
Real Estate AI Orchestrator

This module serves as the central orchestration layer for the real estate analysis system,
integrating all components including market analysis, sentiment analysis, investment confidence,
street-level analysis, and metro-aware investment analysis.
"""

import os
import sys
import json
import logging
from typing import Dict, List, Any, Optional, Tuple, Union
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import dotenv for environment variables
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    logger.warning("dotenv not installed. Environment variables may not be loaded properly.")

# Import OpenAI for intent parsing
try:
    import openai
    from openai import OpenAI
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_AVAILABLE = True
except ImportError:
    logger.warning("OpenAI package not installed. Intent parsing will be limited.")
    OPENAI_AVAILABLE = False

# Import our components with fallbacks for missing modules
try:
    from src.integration.combine_market_and_sentiment import combine_analysis
except ImportError:
    logger.warning("combine_market_and_sentiment module not found. Using mock implementation.")
    def combine_analysis(zip_code: str) -> Dict[str, Any]:
        """Mock implementation of combine_analysis."""
        return {
            "zip": zip_code,
            "market_score": 75.0,
            "reputation_score": 80.0,
            "trend_score": 65.0,
            "econ_score": 70.0,
            "buzz_source": "Mock Data",
            "market_summary": f"Mock market summary for {zip_code}",
            "buzz_summary": f"Mock sentiment summary for {zip_code}"
        }

try:
    from src.analysis.investment_confidence_engine import calculate_investment_confidence, calculate_full_investment_profile
except ImportError:
    logger.warning("investment_confidence_engine module not found. Using mock implementation.")
    def calculate_investment_confidence(market_score, reputation_score, trend_score, econ_score, 
                                      vacancy_penalty=0.0, crime_penalty=0.0, permit_bonus=0.0):
        """Mock implementation of calculate_investment_confidence."""
        base_score = (0.4 * market_score + 0.3 * reputation_score + 0.2 * trend_score + 0.1 * econ_score)
        adjusted_score = base_score - vacancy_penalty - crime_penalty + permit_bonus
        return max(0, min(100, round(adjusted_score, 2)))
    
    def calculate_full_investment_profile(market_score, reputation_score, trend_score, econ_score, adjustments=None):
        """Mock implementation of calculate_full_investment_profile."""
        if adjustments is None:
            adjustments = {}
            
        vacancy_penalty = adjustments.get("vacancy_penalty", 0.0)
        crime_penalty = adjustments.get("crime_penalty", 0.0)
        permit_bonus = adjustments.get("permit_bonus", 0.0)
        
        confidence_score = calculate_investment_confidence(
            market_score, reputation_score, trend_score, econ_score,
            vacancy_penalty, crime_penalty, permit_bonus
        )
        
        # Determine rating based on confidence score
        if confidence_score >= 90:
            rating = "A+"
            recommendation = "Strong Buy"
        elif confidence_score >= 80:
            rating = "A"
            recommendation = "Buy"
        elif confidence_score >= 70:
            rating = "B+"
            recommendation = "Moderate Buy"
        elif confidence_score >= 60:
            rating = "B"
            recommendation = "Hold/Buy"
        elif confidence_score >= 50:
            rating = "C+"
            recommendation = "Hold"
        elif confidence_score >= 40:
            rating = "C"
            recommendation = "Hold/Sell"
        elif confidence_score >= 30:
            rating = "D+"
            recommendation = "Moderate Sell"
        elif confidence_score >= 20:
            rating = "D"
            recommendation = "Sell"
        else:
            rating = "F"
            recommendation = "Strong Sell"
            
        return {
            "confidence_score": confidence_score,
            "rating": rating,
            "recommendation": recommendation,
            "adjustments_applied": {
                "vacancy_penalty": vacancy_penalty,
                "crime_penalty": crime_penalty,
                "permit_bonus": permit_bonus
            }
        }

try:
    from src.utils.zip_to_metro_mapping import get_metro_for_zip, get_data_sources_for_zip
except ImportError:
    logger.warning("zip_to_metro_mapping module not found. Using mock implementation.")
    def get_metro_for_zip(zip_code: str, mapping=None) -> Optional[str]:
        """Mock implementation of get_metro_for_zip."""
        metro_map = {
            "30318": "atlanta", "30312": "atlanta", "30308": "atlanta",
            "11238": "nyc", "11217": "nyc",
            "94110": "sf", "94103": "sf",
            "90210": "la", "90069": "la",
            "60614": "chicago", "60601": "chicago",
            "75201": "dallas", "75202": "dallas",
            "33101": "miami", "33109": "miami"
        }
        return metro_map.get(zip_code)
    
    def get_data_sources_for_zip(zip_code: str, mapping=None) -> List[str]:
        """Mock implementation of get_data_sources_for_zip."""
        metro = get_metro_for_zip(zip_code)
        source_map = {
            "atlanta": ["Reddit", "Twitter"],
            "nyc": ["Reddit", "Twitter", "TikTok"],
            "sf": ["Reddit", "Yelp"],
            "la": ["Reddit", "Twitter", "YouTube"],
            "chicago": ["Reddit", "Facebook"],
            "dallas": ["Reddit", "Nextdoor"],
            "miami": ["Reddit", "Instagram"]
        }
        return source_map.get(metro, ["Reddit"])

try:
    from src.analysis.street_sentiment_analyzer import analyze_street_sentiment, analyze_multiple_streets
except ImportError:
    logger.warning("street_sentiment_analyzer module not found. Using mock implementation.")
    def analyze_street_sentiment(street_name: str, zip_code: str, platform: str = None) -> Dict[str, Any]:
        """Mock implementation of analyze_street_sentiment."""
        metro = get_metro_for_zip(zip_code)
        recommended_platforms = get_data_sources_for_zip(zip_code)
        platform = platform or (recommended_platforms[0] if recommended_platforms else "Reddit")
        
        return {
            "status": "Complete",
            "street": street_name,
            "zip": zip_code,
            "metro": metro,
            "platform": platform,
            "recommended_platforms": recommended_platforms,
            "score": 0.75,  # Mock score between 0-1
            "summary": f"Mock sentiment summary for {street_name} in {zip_code}",
            "posts": [f"Mock post 1 about {street_name}", f"Mock post 2 about {street_name}"]
        }
    
    def analyze_multiple_streets(streets: List[str], zip_code: str) -> Dict[str, Any]:
        """Mock implementation of analyze_multiple_streets."""
        results = {street: analyze_street_sentiment(street, zip_code) for street in streets}
        return {
            "zip": zip_code,
            "metro": get_metro_for_zip(zip_code),
            "street_count": len(streets),
            "success_count": len(streets),
            "average_score": 0.75,  # Mock average
            "streets": results
        }

try:
    from src.integration.metro_aware_investment_analyzer import analyze_zip_with_metro_awareness, generate_metro_investment_report
except ImportError:
    logger.warning("metro_aware_investment_analyzer module not found. Using mock implementation.")
    def analyze_zip_with_metro_awareness(zip_code: str, include_adjustments: bool = True) -> Dict[str, Any]:
        """Mock implementation of analyze_zip_with_metro_awareness."""
        metro = get_metro_for_zip(zip_code)
        base_analysis = combine_analysis(zip_code)
        
        # Mock metro-specific adjustments
        adjustments = {}
        if include_adjustments and metro:
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
        
        # Calculate investment profile
        investment_profile = calculate_full_investment_profile(
            market_score=base_analysis.get("market_score", 0),
            reputation_score=base_analysis.get("reputation_score", 0),
            trend_score=base_analysis.get("trend_score", 0),
            econ_score=base_analysis.get("econ_score", 0),
            adjustments=adjustments
        )
        
        return {
            **base_analysis,
            "metro": metro,
            "recommended_sources": get_data_sources_for_zip(zip_code),
            "investment_profile": investment_profile,
            "metro_adjustments": adjustments
        }
    
    def generate_metro_investment_report(zip_codes: List[str]) -> Dict[str, Any]:
        """Mock implementation of generate_metro_investment_report."""
        results = [analyze_zip_with_metro_awareness(zip_code) for zip_code in zip_codes]
        
        # Group by metro
        metro_groups = {}
        for result in results:
            metro = result.get("metro")
            if metro:
                if metro not in metro_groups:
                    metro_groups[metro] = []
                metro_groups[metro].append(result)
        
        # Calculate metro averages (mock)
        metro_averages = {}
        for metro, metro_results in metro_groups.items():
            metro_averages[metro] = {
                "avg_market_score": 75.0,
                "avg_reputation_score": 80.0,
                "avg_confidence_score": 70.0,
                "zip_count": len(metro_results)
            }
        
        # Rank metros
        ranked_metros = [(metro, data["avg_confidence_score"]) for metro, data in metro_averages.items()]
        ranked_metros.sort(key=lambda x: x[1], reverse=True)
        
        return {
            "individual_results": results,
            "metro_groups": metro_groups,
            "metro_averages": metro_averages,
            "ranked_metros": ranked_metros
        }


def extract_intent(prompt: str) -> Dict[str, Any]:
    """
    Uses GPT-4 to extract intent, zip codes, and target metrics from a natural language prompt.
    
    Args:
        prompt: Natural language prompt from the user
        
    Returns:
        Dictionary with extracted intent, ZIP codes, analysis type, and street names
    """
    if not OPENAI_AVAILABLE:
        # Fallback to basic keyword extraction if OpenAI is not available
        return _extract_intent_basic(prompt)
    
    try:
        system_prompt = (
            "You are a real estate prompt parser. Extract the user's intent, target ZIP codes,"
            " type of analysis (market, trend, sentiment, investment, street), and any street names if present."
            " Return a JSON object with keys: 'intent', 'zips', 'analysis_type', 'streets'."
            " The 'streets' field should be a list of street names or null if none are mentioned."
            " The 'zips' field should be a list of ZIP codes as strings."
            " The 'analysis_type' should be one of: 'market', 'trend', 'sentiment', 'investment', 'street', 'compare'."
        )

        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            max_tokens=300
        )
        
        content = response.choices[0].message.content
        logger.info(f"GPT parsed intent: {content}")
        
        # Convert the JSON string to a Python dictionary
        parsed = json.loads(content)
        return parsed
    except Exception as e:
        logger.error(f"Error in GPT intent parsing: {e}")
        return _extract_intent_basic(prompt)


def _extract_intent_basic(prompt: str) -> Dict[str, Any]:
    """
    Basic keyword-based intent extraction as a fallback.
    
    Args:
        prompt: Natural language prompt from the user
        
    Returns:
        Dictionary with extracted intent, ZIP codes, analysis type, and street names
    """
    prompt_lower = prompt.lower()
    
    # Extract ZIP codes using a simple pattern
    import re
    zip_pattern = r'\b\d{5}\b'
    zips = re.findall(zip_pattern, prompt)
    
    # Extract street names (very basic approach)
    streets = []
    street_indicators = [" st", " street", " ave", " avenue", " blvd", " road", " rd", " lane", " ln", " drive", " dr"]
    words = prompt_lower.split()
    for i, word in enumerate(words):
        for indicator in street_indicators:
            if word.endswith(indicator) and i > 0:
                # Get the previous word as part of the street name
                street_name = words[i-1] + " " + word
                streets.append(street_name.title())
    
    # Determine analysis type based on keywords
    analysis_type = "unknown"
    if "market" in prompt_lower:
        analysis_type = "market"
    elif "trend" in prompt_lower:
        analysis_type = "trend"
    elif "sentiment" in prompt_lower or "buzz" in prompt_lower:
        analysis_type = "sentiment"
    elif "invest" in prompt_lower or "confidence" in prompt_lower:
        analysis_type = "investment"
    elif "street" in prompt_lower:
        analysis_type = "street"
    
    # Check for comparison intent
    if "compare" in prompt_lower or "vs" in prompt_lower or "versus" in prompt_lower:
        analysis_type = "compare"
    
    return {
        "intent": "analyze",
        "zips": zips,
        "analysis_type": analysis_type,
        "streets": streets if streets else None
    }


def real_estate_ai_orchestrator(prompt: str) -> Dict[str, Any]:
    """
    Central agent orchestrator that interprets and routes natural language real estate prompts.
    Handles investment inquiries, neighborhood safety, trend comparisons, and sentiment fusion.
    
    Args:
        prompt: Natural language prompt from the user
        
    Returns:
        Dictionary with analysis results based on the user's intent
    """
    # Extract intent, ZIP codes, and other parameters from the prompt
    parsed = extract_intent(prompt)
    logger.info(f"Parsed intent: {parsed}")
    
    zips = parsed.get("zips", [])
    intent = parsed.get("analysis_type", "unknown")
    streets = parsed.get("streets", [])
    
    # Timestamp for the analysis
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Handle different intents
    if intent == "compare" and len(zips) >= 2:
        # Handle comparison between multiple ZIP codes
        logger.info(f"Comparing ZIP codes: {zips}")
        
        # If streets are specified, compare streets across ZIP codes
        if streets:
            street_zip_pairs = [(street, zip_code) for street in streets for zip_code in zips]
            return {
                "type": "street_comparison",
                "timestamp": timestamp,
                "query": prompt,
                "zips": zips,
                "streets": streets,
                **analyze_streets_in_multiple_zips(street_zip_pairs)
            }
        
        # Otherwise, compare ZIP codes at the neighborhood level
        if "investment" in prompt.lower() or "confidence" in prompt.lower():
            # Generate a metro investment report
            report = generate_metro_investment_report(zips)
            return {
                "type": "metro_investment_comparison",
                "timestamp": timestamp,
                "query": prompt,
                "zips": zips,
                **report
            }
        else:
            # Basic ZIP comparison
            return {
                "type": "zip_comparison",
                "timestamp": timestamp,
                "query": prompt,
                "zips": zips,
                "results": {z: combine_analysis(z) for z in zips}
            }
    
    elif intent == "investment" and zips:
        # Handle investment confidence analysis
        zip_code = zips[0]
        logger.info(f"Analyzing investment confidence for ZIP: {zip_code}")
        
        # Use metro-aware investment analysis
        result = analyze_zip_with_metro_awareness(zip_code)
        
        return {
            "type": "investment_analysis",
            "timestamp": timestamp,
            "query": prompt,
            "zip": zip_code,
            **result
        }
    
    elif intent == "street" and streets and zips:
        # Handle street-level sentiment analysis
        logger.info(f"Analyzing street sentiment for streets: {streets} in ZIP: {zips[0]}")
        
        if len(streets) == 1:
            # Single street analysis
            result = analyze_street_sentiment(streets[0], zips[0])
            return {
                "type": "street_analysis",
                "timestamp": timestamp,
                "query": prompt,
                "zip": zips[0],
                "street": streets[0],
                **result
            }
        else:
            # Multiple streets analysis
            result = analyze_multiple_streets(streets, zips[0])
            return {
                "type": "multi_street_analysis",
                "timestamp": timestamp,
                "query": prompt,
                "zip": zips[0],
                "streets": streets,
                **result
            }
    
    elif intent == "sentiment" and zips:
        # Handle sentiment/buzz analysis
        zip_code = zips[0]
        logger.info(f"Analyzing sentiment for ZIP: {zip_code}")
        
        # If streets are specified, analyze at street level
        if streets:
            return {
                "type": "street_sentiment",
                "timestamp": timestamp,
                "query": prompt,
                "zip": zip_code,
                "streets": streets,
                **analyze_multiple_streets(streets, zip_code)
            }
        
        # Otherwise, analyze at neighborhood level
        data = combine_analysis(zip_code)
        return {
            "type": "neighborhood_sentiment",
            "timestamp": timestamp,
            "query": prompt,
            "zip": zip_code,
            **data
        }
    
    elif intent == "market" and zips:
        # Handle market analysis
        zip_code = zips[0]
        logger.info(f"Analyzing market for ZIP: {zip_code}")
        
        data = combine_analysis(zip_code)
        return {
            "type": "market_analysis",
            "timestamp": timestamp,
            "query": prompt,
            "zip": zip_code,
            **data
        }
    
    elif intent == "trend" and zips:
        # Handle trend analysis
        zip_code = zips[0]
        logger.info(f"Analyzing trends for ZIP: {zip_code}")
        
        data = combine_analysis(zip_code)
        return {
            "type": "trend_analysis",
            "timestamp": timestamp,
            "query": prompt,
            "zip": zip_code,
            **data
        }
    
    # Fallback for unrecognized intents
    return {
        "type": "error",
        "timestamp": timestamp,
        "query": prompt,
        "error": "Could not understand intent or missing required parameters.",
        "parsed_intent": parsed
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
    print("\nud83cudfd9ufe0f Real Estate AI Orchestrator")
    print("=" * 50)
    
    # Test queries
    test_queries = [
        "What is the investment confidence in 90210 right now?",
        "How does 11238 compare to 30318 in terms of neighborhood buzz and trend?",
        "Tell me about the sentiment on Edgewood Ave in 30318",
        "Compare investment potential between 94110 in SF and 11238 in NYC",
        "What's the market analysis for 60614 in Chicago?"
    ]
    
    for query in test_queries:
        print(f"\nud83dudcac Query: {query}")
        response = real_estate_ai_orchestrator(query)
        print(f"\nud83dudcca Response Type: {response.get('type', 'unknown')}")
        
        # Print key information based on response type
        if response.get('type') == 'investment_analysis':
            profile = response.get('investment_profile', {})
            print(f"ZIP: {response.get('zip')}")
            print(f"Metro: {response.get('metro', 'Unknown')}")
            print(f"Confidence Score: {profile.get('confidence_score', 0)}/100")
            print(f"Rating: {profile.get('rating', 'N/A')}")
            print(f"Recommendation: {profile.get('recommendation', 'N/A')}")
        
        elif response.get('type') == 'zip_comparison':
            results = response.get('results', {})
            for zip_code, data in results.items():
                print(f"\nZIP: {zip_code}")
                print(f"Market Score: {data.get('market_score', 0)}")
                print(f"Reputation Score: {data.get('reputation_score', 0)}")
                print(f"Trend Score: {data.get('trend_score', 0)}")
        
        elif response.get('type') == 'street_analysis':
            print(f"Street: {response.get('street')}")
            print(f"ZIP: {response.get('zip')}")
            print(f"Score: {response.get('score', 0) * 100:.1f}/100")
            print(f"Summary: {response.get('summary', 'N/A')}")
        
        elif response.get('type') == 'metro_investment_comparison':
            ranked = response.get('ranked_metros', [])
            print("Metro Rankings:")
            for i, (metro, score) in enumerate(ranked):
                print(f"{i+1}. {metro.upper()}: {score:.1f}/100")
        
        elif response.get('type') == 'error':
            print(f"Error: {response.get('error', 'Unknown error')}")
            
        print("\n" + "-" * 30)
