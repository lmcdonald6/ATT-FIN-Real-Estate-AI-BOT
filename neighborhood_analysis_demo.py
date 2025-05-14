"""
Neighborhood Analysis Infrastructure Demo

This script demonstrates how to use the neighborhood sentiment analysis infrastructure
within the real estate analysis system. It shows how to:

1. Initialize the data collection, analysis, and caching components
2. Retrieve neighborhood sentiment data for properties
3. Integrate sentiment data with property analysis
4. Handle data freshness and caching
"""

import asyncio
import json
import os
import sys
import time
from datetime import datetime
from pprint import pprint

# Ensure data directory exists
os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)

# Import the neighborhood cache
from src.data_management.neighborhood_cache import NeighborhoodCache

# Sample property data
SAMPLE_PROPERTIES = [
    {
        "property_id": "P12345",
        "address": "123 Main St, Atlanta, GA 30308",
        "neighborhood": "Atlanta Beltline",
        "city": "Atlanta",
        "price": 450000,
        "bedrooms": 2,
        "bathrooms": 2,
        "square_feet": 1200,
        "year_built": 2010,
        "property_type": "condo"
    },
    {
        "property_id": "P67890",
        "address": "456 Park Ave, New York, NY 10022",
        "neighborhood": "Midtown",
        "city": "Manhattan",
        "price": 1200000,
        "bedrooms": 1,
        "bathrooms": 1,
        "square_feet": 850,
        "year_built": 1985,
        "property_type": "condo"
    },
    {
        "property_id": "P24680",
        "address": "789 Valencia St, San Francisco, CA 94110",
        "neighborhood": "Mission District",
        "city": "San Francisco",
        "price": 950000,
        "bedrooms": 2,
        "bathrooms": 1,
        "square_feet": 1000,
        "year_built": 1925,
        "property_type": "single_family"
    }
]


class PropertyAnalyzer:
    """
    Demonstrates how to integrate neighborhood sentiment analysis into property analysis.
    """
    
    def __init__(self):
        """Initialize the property analyzer with a neighborhood cache."""
        self.neighborhood_cache = NeighborhoodCache()
    
    async def analyze_property(self, property_data):
        """
        Analyze a property, including neighborhood sentiment.
        
        Args:
            property_data: Dictionary with property information
            
        Returns:
            Dictionary with property analysis results
        """
        # Start with basic property analysis
        analysis = self._analyze_basic_property_data(property_data)
        
        # Add neighborhood sentiment analysis
        neighborhood = property_data.get("neighborhood")
        city = property_data.get("city")
        
        if neighborhood:
            # Get neighborhood data from the cache
            neighborhood_data = await self.neighborhood_cache.get_neighborhood_data(neighborhood, city)
            
            # Extract investment factors from sentiment data
            investment_factors = self._extract_investment_factors(neighborhood_data)
            
            # Add to analysis
            analysis["neighborhood_analysis"] = {
                "sentiment_data": neighborhood_data,
                "investment_factors": investment_factors,
                "data_source": neighborhood_data.get("cache_metadata", {}).get("is_generic", False) and "generic" or "real",
                "data_freshness": self._get_data_freshness(neighborhood_data)
            }
        
        return analysis
    
    def _analyze_basic_property_data(self, property_data):
        """
        Perform basic property analysis.
        
        Args:
            property_data: Dictionary with property information
            
        Returns:
            Dictionary with basic property analysis
        """
        # Calculate price per square foot
        price = property_data.get("price", 0)
        sqft = property_data.get("square_feet", 0)
        price_per_sqft = price / sqft if sqft > 0 else 0
        
        # Calculate property age
        year_built = property_data.get("year_built", 0)
        current_year = datetime.now().year
        property_age = current_year - year_built if year_built > 0 else 0
        
        return {
            "property_id": property_data.get("property_id"),
            "address": property_data.get("address"),
            "neighborhood": property_data.get("neighborhood"),
            "city": property_data.get("city"),
            "metrics": {
                "price": price,
                "price_per_sqft": price_per_sqft,
                "property_age": property_age,
                "bedrooms": property_data.get("bedrooms"),
                "bathrooms": property_data.get("bathrooms"),
                "square_feet": sqft
            },
            "analysis_date": datetime.now().isoformat()
        }
    
    def _extract_investment_factors(self, neighborhood_data):
        """
        Extract investment factors from neighborhood sentiment data.
        
        Args:
            neighborhood_data: Dictionary with neighborhood data
            
        Returns:
            Dictionary with investment factors
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
        
        # If we have generic data, return default factors
        if neighborhood_data.get("cache_metadata", {}).get("is_generic", False):
            return investment_factors
        
        # Extract sentiment score from analysis
        analysis = neighborhood_data.get("analysis", {})
        sentiment = analysis.get("overall_sentiment", {})
        
        if sentiment:
            # Convert sentiment score from -1 to 1 scale to 0 to 10 scale
            compound_score = sentiment.get("score", 0)
            normalized_score = (compound_score + 1) * 5  # Convert from [-1,1] to [0,10]
            investment_factors["sentiment_score"] = normalized_score
            
            # Derive other factors based on score
            if normalized_score >= 8:
                investment_factors["price_trend"] = "rising"
                investment_factors["rental_potential"] = "high"
                investment_factors["development_outlook"] = "positive"
            elif normalized_score >= 6:
                investment_factors["price_trend"] = "stable-to-rising"
                investment_factors["rental_potential"] = "moderate-to-high"
                investment_factors["development_outlook"] = "moderately positive"
            elif normalized_score >= 4:
                investment_factors["price_trend"] = "stable"
                investment_factors["rental_potential"] = "moderate"
                investment_factors["development_outlook"] = "neutral"
            else:
                investment_factors["price_trend"] = "declining"
                investment_factors["rental_potential"] = "low"
                investment_factors["development_outlook"] = "negative"
        
        # Extract aspect sentiment for specific factors
        aspects = analysis.get("aspect_sentiment", {})
        
        # Safety affects both risk and opportunity
        safety = aspects.get("safety", {})
        if safety.get("score", 0) > 0.2:
            investment_factors["opportunity_factors"].append("Good safety perception")
        elif safety.get("score", 0) < -0.2:
            investment_factors["risk_factors"].append("Safety concerns")
        
        # Affordability affects price trend
        affordability = aspects.get("affordability", {})
        if affordability.get("score", 0) < -0.2:
            # Negative affordability score means expensive
            investment_factors["opportunity_factors"].append("Premium location commands higher prices")
            if investment_factors["price_trend"] != "declining":
                investment_factors["price_trend"] = "rising"  # Expensive areas tend to appreciate
        
        # Transportation affects rental potential
        transportation = aspects.get("transportation", {})
        if transportation.get("score", 0) > 0.2:
            investment_factors["opportunity_factors"].append("Good transportation options")
            investment_factors["rental_potential"] = "high"  # Good transport improves rental potential
        elif transportation.get("score", 0) < -0.2:
            investment_factors["risk_factors"].append("Limited transportation options")
        
        # Amenities affect rental potential and development outlook
        amenities = aspects.get("amenities", {})
        if amenities.get("score", 0) > 0.2:
            investment_factors["opportunity_factors"].append("Good local amenities")
            if investment_factors["rental_potential"] != "low":
                investment_factors["rental_potential"] = "high"
        elif amenities.get("score", 0) < -0.2:
            investment_factors["risk_factors"].append("Limited local amenities")
        
        return investment_factors
    
    def _get_data_freshness(self, neighborhood_data):
        """
        Determine the freshness of neighborhood data.
        
        Args:
            neighborhood_data: Dictionary with neighborhood data
            
        Returns:
            String indicating data freshness
        """
        metadata = neighborhood_data.get("cache_metadata", {})
        
        if metadata.get("is_generic", False):
            return "generic"
        elif metadata.get("is_fresh", False):
            return "fresh"
        elif metadata.get("is_stale", False):
            return "stale"
        elif metadata.get("is_expired", False):
            return "expired"
        else:
            return "unknown"
    
    def generate_investment_summary(self, property_analysis):
        """
        Generate a human-readable investment summary for a property.
        
        Args:
            property_analysis: Dictionary with property analysis
            
        Returns:
            Text summary of investment potential
        """
        # Basic property info
        address = property_analysis.get("address", "Unknown address")
        neighborhood = property_analysis.get("neighborhood", "Unknown neighborhood")
        metrics = property_analysis.get("metrics", {})
        
        # Check if we have neighborhood analysis
        neighborhood_analysis = property_analysis.get("neighborhood_analysis", {})
        if not neighborhood_analysis:
            return f"Insufficient data to generate investment summary for {address}."
        
        # Get investment factors
        factors = neighborhood_analysis.get("investment_factors", {})
        data_freshness = neighborhood_analysis.get("data_freshness", "unknown")
        
        # Format price and metrics
        price = metrics.get("price", 0)
        price_formatted = f"${price:,}"
        price_per_sqft = metrics.get("price_per_sqft", 0)
        price_per_sqft_formatted = f"${price_per_sqft:,.2f}"
        
        # Generate summary
        summary = f"""Investment Summary for {address}
Neighborhood: {neighborhood}

Property Details:
- Price: {price_formatted}
- Price per sq ft: {price_per_sqft_formatted}
- Bedrooms: {metrics.get('bedrooms', 0)}
- Bathrooms: {metrics.get('bathrooms', 0)}
- Square feet: {metrics.get('square_feet', 0)}
- Property age: {metrics.get('property_age', 0)} years

Neighborhood Sentiment: {factors.get('sentiment_score', 0):.1f}/10 ({data_freshness} data)
Market Outlook:
- Price trend: {factors.get('price_trend', 'unknown').title()}
- Rental potential: {factors.get('rental_potential', 'unknown').title()}
- Development outlook: {factors.get('development_outlook', 'unknown').title()}

Investment Opportunities:"""
        
        # Add opportunity factors
        opportunities = factors.get("opportunity_factors", [])
        if opportunities:
            for opportunity in opportunities:
                summary += f"\n+ {opportunity}"
        else:
            summary += "\n+ No specific opportunities identified"
        
        # Add risk factors
        summary += "\n\nRisk Factors:"
        risks = factors.get("risk_factors", [])
        if risks:
            for risk in risks:
                summary += f"\n! {risk}"
        else:
            summary += "\n! No specific risks identified"
        
        return summary


async def main():
    """
    Main function to demonstrate the neighborhood analysis infrastructure.
    """
    print("Initializing Neighborhood Analysis Infrastructure...")
    analyzer = PropertyAnalyzer()
    
    # Analyze each property
    print("\nAnalyzing properties with neighborhood sentiment data...")
    analyses = []
    
    for property_data in SAMPLE_PROPERTIES:
        print(f"\nAnalyzing {property_data['address']}...")
        analysis = await analyzer.analyze_property(property_data)
        analyses.append(analysis)
        
        # Print investment summary
        print("\n" + "=" * 50)
        print(analyzer.generate_investment_summary(analysis))
        print("=" * 50)
    
    # Save results to file
    output_file = "property_analysis_results.json"
    with open(output_file, "w") as f:
        json.dump(analyses, f, indent=2)
    print(f"\nAnalysis results saved to {output_file}")


if __name__ == "__main__":
    asyncio.run(main())
