"""
Neighborhood Sentiment Analysis Demo

This script demonstrates how to use the neighborhood sentiment analysis feature
with mock data to avoid unnecessary API calls during testing and development.
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from pprint import pprint

# Ensure the src directory is in the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import the mock sentiment analysis module
from src.utils.neighborhood_sentiment_mock import analyze_neighborhood_sentiment


async def enrich_property_with_sentiment(property_data):
    """
    Enrich property data with neighborhood sentiment analysis.
    
    Args:
        property_data: Dictionary containing property information
        
    Returns:
        Enriched property data with neighborhood insights
    """
    # Extract neighborhood from property data
    neighborhood = property_data.get("neighborhood")
    if not neighborhood:
        print(f"No neighborhood specified for property: {property_data.get('address', 'Unknown')}")
        return property_data
    
    # Get sentiment analysis for the neighborhood
    print(f"\nAnalyzing sentiment for: {neighborhood}")
    sentiment_data = await analyze_neighborhood_sentiment(neighborhood)
    
    # Extract key investment factors from sentiment data
    investment_factors = extract_investment_factors(sentiment_data)
    
    # Add sentiment data to property
    enriched_data = property_data.copy()
    enriched_data["neighborhood_analysis"] = {
        "sentiment_data": sentiment_data,
        "investment_factors": investment_factors
    }
    
    return enriched_data


def extract_investment_factors(sentiment_data):
    """
    Extract key investment factors from sentiment data.
    
    Args:
        sentiment_data: The sentiment analysis data
        
    Returns:
        Dictionary with extracted investment factors
    """
    import re
    
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


async def main():
    """
    Main function to demonstrate the neighborhood sentiment analysis feature.
    """
    # Example properties with different neighborhoods
    properties = [
        {
            "property_id": "P12345",
            "address": "123 Main St, Atlanta, GA 30308",
            "neighborhood": "Atlanta Beltline",
            "price": 450000,
            "bedrooms": 2,
            "bathrooms": 2,
            "square_feet": 1200
        },
        {
            "property_id": "P67890",
            "address": "456 Park Ave, New York, NY 10022",
            "neighborhood": "Midtown Manhattan",
            "price": 1200000,
            "bedrooms": 1,
            "bathrooms": 1,
            "square_feet": 850
        },
        {
            "property_id": "P24680",
            "address": "789 Valencia St, San Francisco, CA 94110",
            "neighborhood": "Mission District San Francisco",
            "price": 950000,
            "bedrooms": 2,
            "bathrooms": 1,
            "square_feet": 1000
        }
    ]
    
    # Enrich each property with neighborhood sentiment analysis
    enriched_properties = []
    for property_data in properties:
        enriched_property = await enrich_property_with_sentiment(property_data)
        enriched_properties.append(enriched_property)
    
    # Display the results
    print("\n=== NEIGHBORHOOD SENTIMENT ANALYSIS RESULTS ===")
    for property_data in enriched_properties:
        print(f"\n{'-'*50}")
        print(f"Property: {property_data['address']}")
        print(f"Neighborhood: {property_data['neighborhood']}")
        
        # Get the investment factors
        factors = property_data["neighborhood_analysis"]["investment_factors"]
        sentiment = property_data["neighborhood_analysis"]["sentiment_data"]
        
        print(f"\nSentiment Score: {factors['sentiment_score']}/10")
        print(f"Price Trend: {factors['price_trend']}")
        print(f"Rental Potential: {factors['rental_potential']}")
        print(f"Development Outlook: {factors['development_outlook']}")
        
        print("\nOpportunity Factors:")
        for factor in factors["opportunity_factors"][:3]:  # Show top 3
            print(f"  + {factor}")
            
        print("\nRisk Factors:")
        for factor in factors["risk_factors"][:3]:  # Show top 3
            print(f"  ! {factor}")
    
    # Save the enriched properties to a JSON file
    output_file = "neighborhood_enriched_properties.json"
    with open(output_file, "w") as f:
        json.dump(enriched_properties, f, indent=2)
    print(f"\nEnriched property data saved to {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
