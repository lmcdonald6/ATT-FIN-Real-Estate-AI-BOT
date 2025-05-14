#!/usr/bin/env python3
"""
Present Inference Layer

This module implements the Present temporal inference layer for the
Real Estate Intelligence Core (REIC), focusing on real-time alerts,
live buzz, and current listings for real estate analysis.
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import base layer
from src.inference.base_layer import InferenceLayer

# Import relevant components
try:
    from src.integration.combine_market_and_sentiment import combine_analysis
    from src.analysis.street_sentiment_analyzer import analyze_street_sentiment, analyze_multiple_streets
    from src.utils.zip_to_metro_mapping import get_metro_for_zip, get_data_sources_for_zip
except ImportError as e:
    logger.warning(f"Could not import component: {e}. Using mock implementations.")
    
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
    
    def analyze_street_sentiment(street_name: str, zip_code: str, platform: str = None) -> Dict[str, Any]:
        """Mock implementation of analyze_street_sentiment."""
        return {
            "status": "Complete",
            "street": street_name,
            "zip": zip_code,
            "metro": "mock_metro",
            "platform": platform or "Reddit",
            "score": 0.75,
            "summary": f"Mock sentiment summary for {street_name} in {zip_code}",
            "posts": [f"Mock post 1 about {street_name}", f"Mock post 2 about {street_name}"]
        }
    
    def analyze_multiple_streets(streets: List[str], zip_code: str) -> Dict[str, Any]:
        """Mock implementation of analyze_multiple_streets."""
        return {
            "zip": zip_code,
            "metro": "mock_metro",
            "street_count": len(streets),
            "success_count": len(streets),
            "average_score": 0.75,
            "streets": {s: analyze_street_sentiment(s, zip_code) for s in streets}
        }
    
    def get_metro_for_zip(zip_code: str) -> Optional[str]:
        """Mock implementation of get_metro_for_zip."""
        return "mock_metro"
    
    def get_data_sources_for_zip(zip_code: str) -> List[str]:
        """Mock implementation of get_data_sources_for_zip."""
        return ["Reddit", "Twitter"]


class PresentInferenceLayer(InferenceLayer):
    """
    Present Inference Layer for real-time alerts, live buzz, and current listings.
    
    This layer focuses on:
    - Current market conditions
    - Real-time sentiment analysis
    - Active listings and inventory
    - Current economic indicators
    """
    
    def __init__(self):
        """
        Initialize the Present inference layer.
        """
        super().__init__("Present")
        self.real_time_data_sources = [
            "current_listings",
            "live_sentiment",
            "market_conditions",
            "economic_indicators"
        ]
    
    def process_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a query using real-time data and analysis.
        
        Args:
            query: The user query to process
            context: Additional context for the query
            
        Returns:
            Dictionary with the processed results
        """
        logger.info(f"Processing query with Present layer: {query}")
        
        # Extract ZIP codes from context
        zip_codes = context.get("zip_codes", [])
        if not zip_codes:
            return {
                "layer": "present",
                "error": "No ZIP codes provided in context",
                "query": query
            }
        
        # Extract streets from context if available
        streets = context.get("streets", [])
        
        # Current timestamp
        timestamp = datetime.now().isoformat()
        
        # Process each ZIP code
        results = {}
        for zip_code in zip_codes:
            # Get current analysis for this ZIP
            current_data = combine_analysis(zip_code)
            
            # Get metro information
            metro = get_metro_for_zip(zip_code)
            data_sources = get_data_sources_for_zip(zip_code)
            
            # Add street-level analysis if streets are provided
            street_analysis = None
            if streets:
                street_analysis = analyze_multiple_streets(streets, zip_code)
            
            # Combine all data
            zip_result = {
                **current_data,
                "metro": metro,
                "data_sources": data_sources,
                "timestamp": timestamp
            }
            
            if street_analysis:
                zip_result["street_analysis"] = street_analysis
            
            # Add to results
            results[zip_code] = zip_result
        
        # Prepare response
        response = {
            "layer": "present",
            "query": query,
            "timestamp": timestamp,
            "results": results
        }
        
        # Add real-time insights
        response["insights"] = self._generate_real_time_insights(results, query)
        
        return response
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities this layer provides.
        
        Returns:
            List of capability strings
        """
        return [
            "current market",
            "live data",
            "real-time sentiment",
            "active listings",
            "current conditions",
            "today's market",
            "present state",
            "current buzz"
        ]
    
    def is_relevant_for_query(self, query: str) -> bool:
        """
        Determine if this layer is relevant for the given query.
        
        Args:
            query: The user query to check
            
        Returns:
            True if this layer is relevant, False otherwise
        """
        # Check for time-related keywords
        time_keywords = [
            "current", "now", "today", "present", "real-time",
            "live", "active", "right now", "currently", "at the moment"
        ]
        
        query_lower = query.lower()
        
        # Check base capabilities
        if super().is_relevant_for_query(query):
            return True
        
        # Check time keywords
        for keyword in time_keywords:
            if keyword in query_lower:
                return True
        
        # If no time frame is specified, default to present
        time_frame_words = [
            "history", "historical", "past", "previous", "before",
            "future", "predict", "forecast", "projection", "will be"
        ]
        
        for keyword in time_frame_words:
            if keyword in query_lower:
                return False
        
        # Default to present if no time frame is specified
        return True
    
    def _generate_real_time_insights(self, results: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """
        Generate insights from real-time data.
        
        Args:
            results: The real-time results by ZIP code
            query: The original user query
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # For each ZIP code, analyze the current conditions
        for zip_code, data in results.items():
            # Generate insights based on scores
            market_score = data.get("market_score", 0)
            reputation_score = data.get("reputation_score", 0)
            trend_score = data.get("trend_score", 0)
            econ_score = data.get("econ_score", 0)
            
            # Market score insight
            if market_score > 80:
                insights.append({
                    "zip": zip_code,
                    "metric": "market_score",
                    "value": market_score,
                    "insight": f"Strong current market conditions in {zip_code} with a score of {market_score}/100."
                })
            elif market_score < 40:
                insights.append({
                    "zip": zip_code,
                    "metric": "market_score",
                    "value": market_score,
                    "insight": f"Weak current market conditions in {zip_code} with a score of {market_score}/100."
                })
            
            # Reputation score insight
            if reputation_score > 80:
                insights.append({
                    "zip": zip_code,
                    "metric": "reputation_score",
                    "value": reputation_score,
                    "insight": f"Excellent current reputation in {zip_code} with a score of {reputation_score}/100."
                })
            elif reputation_score < 40:
                insights.append({
                    "zip": zip_code,
                    "metric": "reputation_score",
                    "value": reputation_score,
                    "insight": f"Poor current reputation in {zip_code} with a score of {reputation_score}/100."
                })
            
            # Street-level insights
            street_analysis = data.get("street_analysis", {})
            streets_data = street_analysis.get("streets", {})
            
            if streets_data:
                # Find best and worst streets
                street_scores = [(s, d.get("score", 0)) for s, d in streets_data.items()]
                street_scores.sort(key=lambda x: x[1], reverse=True)
                
                if street_scores:
                    best_street, best_score = street_scores[0]
                    insights.append({
                        "zip": zip_code,
                        "metric": "street_sentiment",
                        "street": best_street,
                        "value": best_score * 100,  # Convert to 0-100 scale
                        "insight": f"{best_street} currently has the highest sentiment in {zip_code} with a score of {best_score * 100:.1f}/100."
                    })
                    
                    if len(street_scores) > 1:
                        worst_street, worst_score = street_scores[-1]
                        insights.append({
                            "zip": zip_code,
                            "metric": "street_sentiment",
                            "street": worst_street,
                            "value": worst_score * 100,  # Convert to 0-100 scale
                            "insight": f"{worst_street} currently has the lowest sentiment in {zip_code} with a score of {worst_score * 100:.1f}/100."
                        })
        
        return insights
