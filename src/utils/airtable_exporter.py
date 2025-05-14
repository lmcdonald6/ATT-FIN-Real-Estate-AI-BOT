#!/usr/bin/env python3
"""
Airtable Exporter

This utility module provides functionality to export neighborhood analysis results
to Airtable for tracking, visualization, and sharing with stakeholders.
"""

import json
import logging
import os
from datetime import datetime
from typing import Dict, List, Any, Optional, Union

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from pyairtable import Table, Api
    from pyairtable.formulas import match
except ImportError:
    logger.warning("pyairtable not installed. Run 'pip install pyairtable' to use this module.")

# Environment variables for Airtable configuration
AIRTABLE_API_KEY = os.environ.get("AIRTABLE_API_KEY")
AIRTABLE_BASE_ID = os.environ.get("AIRTABLE_BASE_ID")
AIRTABLE_NEIGHBORHOODS_TABLE = os.environ.get("AIRTABLE_NEIGHBORHOODS_TABLE", "Neighborhoods")
AIRTABLE_ANALYSIS_TABLE = os.environ.get("AIRTABLE_ANALYSIS_TABLE", "Analysis Results")


class AirtableExporter:
    """Class for exporting neighborhood analysis data to Airtable."""
    
    def __init__(self, api_key: Optional[str] = None, base_id: Optional[str] = None):
        """
        Initialize the Airtable exporter.
        
        Args:
            api_key: Airtable API key (defaults to AIRTABLE_API_KEY environment variable)
            base_id: Airtable base ID (defaults to AIRTABLE_BASE_ID environment variable)
        """
        self.api_key = api_key or AIRTABLE_API_KEY
        self.base_id = base_id or AIRTABLE_BASE_ID
        
        if not self.api_key or not self.base_id:
            logger.warning("Airtable API key or base ID not provided. Set AIRTABLE_API_KEY and AIRTABLE_BASE_ID environment variables.")
        
        # Initialize Airtable API client if credentials are available
        self.api = Api(self.api_key) if self.api_key else None
    
    def _get_table(self, table_name: str) -> Optional[Table]:
        """
        Get an Airtable table object.
        
        Args:
            table_name: Name of the Airtable table
            
        Returns:
            Table object or None if API client is not initialized
        """
        if not self.api or not self.base_id:
            logger.error("Airtable API client not initialized. Check API key and base ID.")
            return None
        
        return Table(self.api_key, self.base_id, table_name)
    
    def export_neighborhood(self, zip_code: str, city: str, state: str, data: Dict[str, Any]) -> Optional[str]:
        """
        Export or update a neighborhood record in Airtable.
        
        Args:
            zip_code: ZIP code of the neighborhood
            city: City name
            state: State abbreviation
            data: Additional neighborhood data
            
        Returns:
            Record ID of the created or updated record, or None if export failed
        """
        table = self._get_table(AIRTABLE_NEIGHBORHOODS_TABLE)
        if not table:
            return None
        
        try:
            # Check if neighborhood already exists
            formula = match({"ZIP": zip_code})
            existing_records = table.all(formula=formula)
            
            # Prepare record data
            record_data = {
                "ZIP": zip_code,
                "City": city,
                "State": state,
                "Last Updated": datetime.now().isoformat()
            }
            
            # Add any additional fields from data
            if "median_price" in data:
                record_data["Median Price"] = data["median_price"]
            if "market_score" in data:
                record_data["Market Score"] = data["market_score"]
            if "reputation_score" in data.get("sentiment", {}).get("reputation", {}):
                record_data["Reputation Score"] = data["sentiment"]["reputation"]["overall_score"] * 100
            if "investment" in data and "score" in data["investment"]:
                record_data["Investment Score"] = data["investment"]["score"]
                record_data["Investment Rating"] = data["investment"]["rating"]
                record_data["Recommendation"] = data["investment"]["recommendation"]
            
            # Create or update record
            if existing_records:
                record_id = existing_records[0]["id"]
                table.update(record_id, record_data)
                logger.info(f"Updated neighborhood record for ZIP {zip_code} (ID: {record_id})")
            else:
                created_record = table.create(record_data)
                record_id = created_record["id"]
                logger.info(f"Created new neighborhood record for ZIP {zip_code} (ID: {record_id})")
            
            return record_id
            
        except Exception as e:
            logger.error(f"Error exporting neighborhood to Airtable: {str(e)}")
            return None
    
    def export_analysis_result(self, zip_code: str, analysis_data: Dict[str, Any]) -> Optional[str]:
        """
        Export an analysis result to Airtable.
        
        Args:
            zip_code: ZIP code of the analyzed neighborhood
            analysis_data: Analysis result data
            
        Returns:
            Record ID of the created record, or None if export failed
        """
        table = self._get_table(AIRTABLE_ANALYSIS_TABLE)
        if not table:
            return None
        
        try:
            # Prepare record data
            record_data = {
                "ZIP": zip_code,
                "Analysis Date": datetime.now().isoformat(),
                "Analysis Type": "Combined Market & Sentiment"
            }
            
            # Add market data
            if "market" in analysis_data:
                market = analysis_data["market"]
                record_data["Median Price"] = market.get("median_price")
                record_data["Price Growth (1yr)"] = market.get("price_growth_1yr")
                record_data["Rental Yield"] = market.get("rental_yield")
                record_data["Days on Market"] = market.get("days_on_market")
                record_data["Market Score"] = market.get("market_score")
            
            # Add sentiment data
            if "sentiment" in analysis_data and "reputation" in analysis_data["sentiment"]:
                reputation = analysis_data["sentiment"]["reputation"]
                record_data["Sentiment Score"] = reputation.get("overall_score", 0) * 100
                record_data["Sentiment Confidence"] = reputation.get("confidence_score")
                record_data["Data Source"] = analysis_data["sentiment"].get("source")
                
                # Add summary if available
                if "summary" in reputation:
                    record_data["Sentiment Summary"] = reputation["summary"]
            
            # Add investment data
            if "investment" in analysis_data:
                investment = analysis_data["investment"]
                record_data["Investment Score"] = investment.get("score")
                record_data["Investment Rating"] = investment.get("rating")
                record_data["Recommendation"] = investment.get("recommendation")
            
            # Create record
            created_record = table.create(record_data)
            record_id = created_record["id"]
            logger.info(f"Created new analysis record for ZIP {zip_code} (ID: {record_id})")
            
            return record_id
            
        except Exception as e:
            logger.error(f"Error exporting analysis result to Airtable: {str(e)}")
            return None
    
    def export_combined_analysis(self, analysis_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Export a combined analysis result to Airtable, updating both the neighborhood
        and analysis tables.
        
        Args:
            analysis_data: Combined analysis result data
            
        Returns:
            Dictionary with export results
        """
        zip_code = analysis_data.get("zip_code")
        if not zip_code:
            logger.error("ZIP code not found in analysis data")
            return {"success": False, "error": "ZIP code not found"}
        
        # Extract city and state (mock data if not available)
        city = analysis_data.get("city", "Unknown")
        state = analysis_data.get("state", "XX")
        
        # Export to neighborhood table
        neighborhood_id = self.export_neighborhood(zip_code, city, state, analysis_data)
        
        # Export to analysis table
        analysis_id = self.export_analysis_result(zip_code, analysis_data)
        
        return {
            "success": bool(neighborhood_id and analysis_id),
            "neighborhood_id": neighborhood_id,
            "analysis_id": analysis_id,
            "zip_code": zip_code
        }
    
    def export_batch(self, analysis_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Export a batch of analysis results to Airtable.
        
        Args:
            analysis_results: List of analysis result data
            
        Returns:
            Dictionary with export results
        """
        results = []
        success_count = 0
        
        for analysis in analysis_results:
            result = self.export_combined_analysis(analysis)
            results.append(result)
            
            if result.get("success", False):
                success_count += 1
        
        return {
            "total": len(analysis_results),
            "success": success_count,
            "results": results
        }


def export_to_airtable(analysis_data: Union[Dict[str, Any], List[Dict[str, Any]]]) -> Dict[str, Any]:
    """
    Export analysis data to Airtable.
    
    Args:
        analysis_data: Single analysis result or list of analysis results
        
    Returns:
        Dictionary with export results
    """
    exporter = AirtableExporter()
    
    if isinstance(analysis_data, list):
        return exporter.export_batch(analysis_data)
    else:
        result = exporter.export_combined_analysis(analysis_data)
        return {
            "total": 1,
            "success": int(result.get("success", False)),
            "results": [result]
        }


def setup_airtable_tables():
    """
    Set up the required Airtable tables with the correct fields.
    This is a helper function to create the tables if they don't exist.
    
    Note: Airtable API doesn't support table creation, so this function
    prints instructions for manual table setup.
    """
    print("\nud83dudcca Airtable Table Setup Instructions")
    print("\nThe Airtable API doesn't support table creation, so you'll need to create the tables manually.")
    print("Here's how to set up the required tables:")
    
    print("\n1. ud83cudfe0 Neighborhoods Table (Name: 'Neighborhoods')")
    print("   - ZIP (Single line text, Primary field)")
    print("   - City (Single line text)")
    print("   - State (Single line text)")
    print("   - Median Price (Number, currency)")
    print("   - Market Score (Number, 0-100)")
    print("   - Reputation Score (Number, 0-100)")
    print("   - Investment Score (Number, 0-100)")
    print("   - Investment Rating (Single line text)")
    print("   - Recommendation (Single select: Strong Buy, Buy, Hold, Neutral, Avoid)")
    print("   - Last Updated (Date)")
    
    print("\n2. ud83dudcc8 Analysis Results Table (Name: 'Analysis Results')")
    print("   - ZIP (Single line text, Primary field)")
    print("   - Analysis Date (Date)")
    print("   - Analysis Type (Single select: Market, Sentiment, Combined)")
    print("   - Median Price (Number, currency)")
    print("   - Price Growth (1yr) (Number, percentage)")
    print("   - Rental Yield (Number, percentage)")
    print("   - Days on Market (Number)")
    print("   - Market Score (Number, 0-100)")
    print("   - Sentiment Score (Number, 0-100)")
    print("   - Sentiment Confidence (Number, 0-1)")
    print("   - Data Source (Single line text)")
    print("   - Sentiment Summary (Long text)")
    print("   - Investment Score (Number, 0-100)")
    print("   - Investment Rating (Single line text)")
    print("   - Recommendation (Single select: Strong Buy, Buy, Hold, Neutral, Avoid)")
    
    print("\nud83dudd11 Don't forget to set your Airtable API key and base ID as environment variables:")
    print("   - AIRTABLE_API_KEY")
    print("   - AIRTABLE_BASE_ID")
    print("   - AIRTABLE_NEIGHBORHOODS_TABLE (optional, defaults to 'Neighborhoods')")
    print("   - AIRTABLE_ANALYSIS_TABLE (optional, defaults to 'Analysis Results')")


if __name__ == "__main__":
    # Display setup instructions
    setup_airtable_tables()
    
    # Check if API key and base ID are set
    if not AIRTABLE_API_KEY or not AIRTABLE_BASE_ID:
        print("\nu26a0ufe0f Airtable API key or base ID not set. Please set the environment variables.")
    else:
        print("\nu2705 Airtable API key and base ID are set.")
        
        # Test connection
        try:
            api = Api(AIRTABLE_API_KEY)
            base = api.base(AIRTABLE_BASE_ID)
            print(f"\nu2705 Successfully connected to Airtable base: {AIRTABLE_BASE_ID}")
            
            # List tables in the base
            print("\nud83dudcc2 Available tables in this base:")
            for table in base.tables:
                print(f"   - {table['name']}")
                
        except Exception as e:
            print(f"\nu274c Error connecting to Airtable: {str(e)}")
