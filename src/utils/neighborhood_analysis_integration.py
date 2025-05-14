"""
Neighborhood Analysis Integration Module

This module provides integration between the neighborhood sentiment analysis
and the main real estate analysis system, following microservice principles.
"""

import logging
import json
import os
import asyncio
from typing import Dict, Any, Optional, List, Union

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NeighborhoodAnalysisService:
    """Service for integrating neighborhood sentiment analysis with property data."""
    
    def __init__(self, use_mock: bool = True, cache_dir: str = "data/neighborhood_cache"):
        """
        Initialize the neighborhood analysis service.
        
        Args:
            use_mock: Whether to use mock data (True) or real API calls (False)
            cache_dir: Directory to cache neighborhood analysis results
        """
        self.use_mock = use_mock
        self.cache_dir = cache_dir
        
        # Create cache directory if it doesn't exist
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Import the appropriate module based on mock setting
        if self.use_mock:
            from src.utils.neighborhood_sentiment_mock import analyze_neighborhood_sentiment
        else:
            try:
                from src.utils.neighborhood_sentiment_v2 import analyze_neighborhood_sentiment
            except ImportError:
                logger.warning("Could not import real sentiment analysis module, falling back to mock")
                from src.utils.neighborhood_sentiment_mock import analyze_neighborhood_sentiment
        
        self.analyze_sentiment = analyze_neighborhood_sentiment
    
    async def get_neighborhood_insights(self, location: str, force_refresh: bool = False) -> Dict[str, Any]:
        """
        Get neighborhood insights for a location, using cached data if available.
        
        Args:
            location: The neighborhood or location name
            force_refresh: Whether to force a refresh of the data even if cached
            
        Returns:
            Dictionary containing neighborhood insights
        """
        cache_file = os.path.join(self.cache_dir, f"{location.lower().replace(' ', '_')}.json")
        
        # Check if we have cached data and should use it
        if os.path.exists(cache_file) and not force_refresh:
            try:
                with open(cache_file, 'r') as f:
                    cached_data = json.load(f)
                logger.info(f"Using cached neighborhood data for {location}")
                return cached_data
            except Exception as e:
                logger.error(f"Error reading cache file: {str(e)}")
        
        # Get fresh data
        logger.info(f"Getting fresh neighborhood data for {location}")
        sentiment_data = await self.analyze_sentiment(location)
        
        # Cache the data
        try:
            with open(cache_file, 'w') as f:
                json.dump(sentiment_data, f, indent=2)
        except Exception as e:
            logger.error(f"Error writing cache file: {str(e)}")
        
        return sentiment_data
    
    def extract_investment_factors(self, sentiment_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract key investment factors from sentiment data.
        
        Args:
            sentiment_data: The sentiment analysis data
            
        Returns:
            Dictionary with extracted investment factors
        """
        # Initialize default values
        investment_factors = {
            "sentiment_score": 5,  # Default neutral score
            "price_trend": "stable",
            "rental_potential": "moderate",
            "development_outlook": "neutral",
            "risk_factors": [],
            "opportunity_factors": []
        }
        
        # If we have valid sentiment data, try to extract investment factors
        if sentiment_data.get("success") and sentiment_data.get("sentiment_summary"):
            summary = sentiment_data["sentiment_summary"]
            
            # Extract sentiment score if present (format: "Overall sentiment score: X/10")
            import re
            score_match = re.search(r"sentiment score: (\d+(?:\.\d+)?)/10", summary)
            if score_match:
                try:
                    score = float(score_match.group(1))
                    investment_factors["sentiment_score"] = score
                    
                    # Derive other factors based on score
                    if score >= 8:
                        investment_factors["price_trend"] = "rising"
                        investment_factors["rental_potential"] = "high"
                        investment_factors["development_outlook"] = "positive"
                    elif score >= 6:
                        investment_factors["price_trend"] = "stable-to-rising"
                        investment_factors["rental_potential"] = "moderate-to-high"
                        investment_factors["development_outlook"] = "moderately positive"
                    elif score >= 4:
                        investment_factors["price_trend"] = "stable"
                        investment_factors["rental_potential"] = "moderate"
                        investment_factors["development_outlook"] = "neutral"
                    else:
                        investment_factors["price_trend"] = "declining"
                        investment_factors["rental_potential"] = "low"
                        investment_factors["development_outlook"] = "negative"
                except:
                    pass
            
            # Extract risk and opportunity factors from the summary
            # Look for sections like "Negative aspects:" and "Positive aspects:"
            neg_section_match = re.search(r"Negative aspects:[\s\S]*?(?=\n\n|$)", summary)
            if neg_section_match:
                neg_section = neg_section_match.group(0)
                risk_factors = re.findall(r"- (.+?)(?=\n|$)", neg_section)
                if risk_factors:
                    investment_factors["risk_factors"] = risk_factors
            
            pos_section_match = re.search(r"Positive aspects:[\s\S]*?(?=\n\n|$)", summary)
            if pos_section_match:
                pos_section = pos_section_match.group(0)
                opportunity_factors = re.findall(r"- (.+?)(?=\n|$)", pos_section)
                if opportunity_factors:
                    investment_factors["opportunity_factors"] = opportunity_factors
        
        return investment_factors
    
    async def enrich_property_data(self, property_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enrich property data with neighborhood sentiment analysis.
        
        Args:
            property_data: Dictionary containing property information
            
        Returns:
            Enriched property data with neighborhood insights
        """
        # Extract location information from property data
        location = None
        if property_data.get("neighborhood"):
            location = property_data["neighborhood"]
        elif property_data.get("address"):
            # Try to extract neighborhood from address
            address_parts = property_data["address"].split(",")
            if len(address_parts) >= 2:
                # Use city as fallback
                location = address_parts[1].strip()
        
        if not location:
            logger.warning("Could not determine location from property data")
            return property_data
        
        # Get neighborhood insights
        neighborhood_data = await self.get_neighborhood_insights(location)
        
        # Extract investment factors
        investment_factors = self.extract_investment_factors(neighborhood_data)
        
        # Enrich property data
        enriched_data = property_data.copy()
        enriched_data["neighborhood_analysis"] = {
            "sentiment_data": neighborhood_data,
            "investment_factors": investment_factors
        }
        
        return enriched_data


# Example usage
async def main():
    from pprint import pprint
    import asyncio
    
    # Initialize service
    service = NeighborhoodAnalysisService(use_mock=True)
    
    # Example property data
    property_data = {
        "property_id": "P12345",
        "address": "123 Main St, Atlanta, GA 30308",
        "neighborhood": "Atlanta Beltline",
        "price": 450000,
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1200
    }
    
    # Enrich property data
    enriched_data = await service.enrich_property_data(property_data)
    
    # Print enriched data (investment factors only for brevity)
    print("\nProperty with Neighborhood Analysis:")
    print(f"Property: {enriched_data['address']}")
    print(f"Neighborhood: {enriched_data['neighborhood']}")
    print("\nInvestment Factors:")
    pprint(enriched_data["neighborhood_analysis"]["investment_factors"])
    
    # Example of getting just the neighborhood insights
    print("\nDetailed Neighborhood Insights:")
    insights = await service.get_neighborhood_insights("Midtown Manhattan")
    print(f"Sentiment Score: {service.extract_investment_factors(insights)['sentiment_score']}/10")
    print(f"Summary excerpt: {insights['sentiment_summary'][:200]}...")


if __name__ == "__main__":
    asyncio.run(main())
