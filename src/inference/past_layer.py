#!/usr/bin/env python3
"""
Past Inference Layer

This module implements the Past temporal inference layer for the
Real Estate Intelligence Core (REIC), focusing on historical context,
cycles, and anchor points for real estate analysis.
"""

import os
import sys
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

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
except ImportError:
    logger.warning("Could not import combine_analysis. Using mock implementation.")
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


class PastInferenceLayer(InferenceLayer):
    """
    Past Inference Layer for historical context, cycles, and anchor points.
    
    This layer focuses on:
    - Historical price trends
    - Past market cycles
    - Historical sentiment analysis
    - Comparative historical performance
    """
    
    def __init__(self):
        """
        Initialize the Past inference layer.
        """
        super().__init__("Past")
        self.historical_data_sources = [
            "price_history",
            "sentiment_archives",
            "market_cycles",
            "economic_indicators_history"
        ]
    
    def process_query(self, query: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a query using historical data and analysis.
        
        Args:
            query: The user query to process
            context: Additional context for the query
            
        Returns:
            Dictionary with the processed results
        """
        logger.info(f"Processing query with Past layer: {query}")
        
        # Extract ZIP codes from context
        zip_codes = context.get("zip_codes", [])
        if not zip_codes:
            return {
                "layer": "past",
                "error": "No ZIP codes provided in context",
                "query": query
            }
        
        # Extract time range from context or default to 5 years
        years_back = context.get("years_back", 5)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365 * years_back)
        
        # Process each ZIP code
        results = {}
        for zip_code in zip_codes:
            # Get historical analysis for this ZIP
            historical_data = self._get_historical_data(zip_code, start_date, end_date)
            
            # Add to results
            results[zip_code] = historical_data
        
        # Prepare response
        response = {
            "layer": "past",
            "query": query,
            "time_range": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat(),
                "years": years_back
            },
            "results": results
        }
        
        # Add historical insights
        response["insights"] = self._generate_historical_insights(results, query)
        
        return response
    
    def get_capabilities(self) -> List[str]:
        """
        Get the list of capabilities this layer provides.
        
        Returns:
            List of capability strings
        """
        return [
            "historical trends",
            "price history",
            "past performance",
            "market cycles",
            "previous years",
            "historical comparison",
            "past sentiment",
            "historical data"
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
            "history", "historical", "past", "previous", "before",
            "last year", "five years", "decade", "trend", "cycle"
        ]
        
        query_lower = query.lower()
        
        # Check base capabilities
        if super().is_relevant_for_query(query):
            return True
        
        # Check time keywords
        for keyword in time_keywords:
            if keyword in query_lower:
                return True
        
        return False
    
    def _get_historical_data(self, zip_code: str, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """
        Get historical data for a ZIP code over a specified time range.
        
        Args:
            zip_code: The ZIP code to analyze
            start_date: Start date for historical data
            end_date: End date for historical data
            
        Returns:
            Dictionary with historical data
        """
        # This would typically query a database or API for historical data
        # For now, we'll use a mock implementation
        
        # Get current analysis as a baseline
        current_data = combine_analysis(zip_code)
        
        # Generate mock historical data points
        historical_points = []
        current_date = start_date
        while current_date <= end_date:
            # Create a data point with some random variation
            import random
            variation = (random.random() - 0.5) * 20  # -10 to +10
            
            data_point = {
                "date": current_date.isoformat(),
                "market_score": max(0, min(100, current_data.get("market_score", 75) + variation)),
                "reputation_score": max(0, min(100, current_data.get("reputation_score", 80) + variation)),
                "trend_score": max(0, min(100, current_data.get("trend_score", 65) + variation)),
                "econ_score": max(0, min(100, current_data.get("econ_score", 70) + variation))
            }
            
            historical_points.append(data_point)
            
            # Move to next quarter
            current_date += timedelta(days=90)
        
        return {
            "zip": zip_code,
            "data_points": historical_points,
            "sources": self.historical_data_sources,
            "summary": f"Historical analysis for {zip_code} from {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
        }
    
    def _generate_historical_insights(self, results: Dict[str, Any], query: str) -> List[Dict[str, Any]]:
        """
        Generate insights from historical data.
        
        Args:
            results: The historical results by ZIP code
            query: The original user query
            
        Returns:
            List of insight dictionaries
        """
        insights = []
        
        # For each ZIP code, analyze the historical trends
        for zip_code, data in results.items():
            data_points = data.get("data_points", [])
            
            if not data_points:
                continue
            
            # Calculate trend directions
            first_point = data_points[0] if data_points else {}
            last_point = data_points[-1] if data_points else {}
            
            for metric in ["market_score", "reputation_score", "trend_score", "econ_score"]:
                first_value = first_point.get(metric, 0)
                last_value = last_point.get(metric, 0)
                
                if first_value == 0 or last_value == 0:
                    continue
                
                change = last_value - first_value
                percent_change = (change / first_value) * 100
                
                direction = "improved" if change > 0 else "declined"
                
                insight = {
                    "zip": zip_code,
                    "metric": metric,
                    "direction": direction,
                    "change": round(change, 2),
                    "percent_change": round(percent_change, 2),
                    "insight": f"{metric.replace('_', ' ').title()} has {direction} by {abs(round(percent_change, 2))}% over the analyzed period."
                }
                
                insights.append(insight)
        
        return insights
