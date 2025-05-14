#!/usr/bin/env python3
"""
Airtable Exporter

This module exports neighborhood analysis results to Airtable for tracking and visualization.
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    from pyairtable import Table
    from dotenv import load_dotenv
except ImportError:
    logger.error("Required packages not installed. Run 'pip install pyairtable python-dotenv'")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Airtable configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Neighborhood Scores")


def export_to_airtable(results: List[Dict[str, Any]], include_timestamp: bool = True) -> Dict[str, Any]:
    """
    Pushes a list of combined analysis results to Airtable.
    Each result must include keys: zip, market_score, reputation_score, etc.
    
    Args:
        results: List of analysis results to export
        include_timestamp: Whether to include a timestamp in the records
        
    Returns:
        Dictionary with export results
    """
    if not API_KEY or not BASE_ID:
        error_msg = "Airtable API key or base ID not set. Check your .env file."
        logger.error(error_msg)
        print(f"\n❌ {error_msg}")
        return {"success": 0, "total": len(results), "error": error_msg}
    
    table = Table(API_KEY, BASE_ID, TABLE_NAME)
    success_count = 0
    sync_status = []
    
    for res in results:
        # Create record with required fields
        record = {
            "ZIP": res.get("zip"),
            "Market Score": res.get("market_score"),
            "Trend Score": res.get("trend_score"),
            "Econ Score": res.get("econ_score"),
            "Reputation Score": res.get("reputation_score"),
            "Buzz Source": res.get("buzz_source"),
            "Market Summary": res.get("market_summary"),
            "Buzz Summary": res.get("buzz_summary")
        }
        
        # Add timestamp if requested
        if include_timestamp:
            record["Last Synced"] = datetime.now().isoformat()
        
        # Add investment data if available
        if "investment_score" in res:
            record["Investment Score"] = res.get("investment_score")
        if "investment_rating" in res:
            record["Investment Rating"] = res.get("investment_rating")
        if "recommendation" in res:
            record["Recommendation"] = res.get("recommendation")
        
        try:
            # Check if record already exists
            existing = table.all(formula=f"{{ZIP}} = '{res.get('zip')}'")  # noqa
            
            if existing:
                # Update existing record
                record_id = existing[0]["id"]
                table.update(record_id, record)
                status = "updated"
            else:
                # Create new record
                created = table.create(record)
                record_id = created["id"]
                status = "created"
            
            success_count += 1
            sync_status.append({"zip": res.get("zip"), "status": status, "id": record_id})
            
        except Exception as e:
            error = str(e)
            logger.error(f"Failed to sync ZIP {res.get('zip')}: {error}")
            print(f"❌ Failed to sync ZIP {res.get('zip')}: {error}")
            sync_status.append({"zip": res.get("zip"), "status": "error", "error": error})
    
    print(f"\n✅ Synced {success_count}/{len(results)} records to Airtable")
    
    return {
        "success": success_count,
        "total": len(results),
        "sync_status": sync_status
    }


def export_to_csv(results: List[Dict[str, Any]], filename: Optional[str] = None) -> str:
    """
    Export analysis results to a CSV file.
    
    Args:
        results: List of analysis results to export
        filename: Output filename (optional)
        
    Returns:
        Path to the exported CSV file
    """
    import csv
    from datetime import datetime
    
    if not filename:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"neighborhood_analysis_{timestamp}.csv"
    
    # Ensure the output directory exists
    output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "output")
    os.makedirs(output_dir, exist_ok=True)
    
    output_path = os.path.join(output_dir, filename)
    
    # Define CSV headers based on the first result
    if not results:
        return output_path
    
    # Get all possible keys from all results
    all_keys = set()
    for res in results:
        all_keys.update(res.keys())
    
    # Filter out internal keys that start with underscore
    headers = [key for key in all_keys if not key.startswith('_')]
    
    # Write to CSV
    with open(output_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=headers, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)
    
    logger.info(f"Exported results to {output_path}")
    print(f"\n📄 Exported results to {output_path}")
    
    return output_path


def setup_airtable():
    """
    Check Airtable configuration and print setup instructions if needed.
    """
    if not API_KEY or not BASE_ID:
        print("\n⚠️ Airtable configuration not found. Please set up your .env file with:")
        print("```")
        print("AIRTABLE_API_KEY=your_token")
        print("AIRTABLE_BASE_ID=your_base_id")
        print("AIRTABLE_TABLE_NAME=Neighborhood Scores")
        print("```")
        print("\nYou can get these values from your Airtable account.")
        return False
    
    print("\n✅ Airtable configuration found!")
    print(f"API Key: {'*' * (len(API_KEY) - 4)}{API_KEY[-4:]}")
    print(f"Base ID: {BASE_ID}")
    print(f"Table Name: {TABLE_NAME}")
    
    # Test connection
    try:
        table = Table(API_KEY, BASE_ID, TABLE_NAME)
        # Just check if we can access the table
        table.all(max_records=1)
        print("\n✅ Successfully connected to Airtable!")
        return True
    except Exception as e:
        print(f"\n❌ Error connecting to Airtable: {str(e)}")
        return False


if __name__ == "__main__":
    # Check if Airtable is configured
    setup_airtable()
    
    # If configuration is valid, run a test export
    if API_KEY and BASE_ID:
        try:
            # Import the combine_analysis function
            sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            if sys_path not in sys.path:
                sys.path.append(sys_path)
            
            from src.integration.combine_market_and_sentiment import combine_analysis
            
            print("\n🔄 Running test export with sample ZIP codes...")
            zips = ["30318", "11238", "90210"]
            
            print("\n📊 Analyzing ZIP codes...")
            records = [combine_analysis(z) for z in zips]
            
            # Export to Airtable
            print("\n📤 Exporting to Airtable...")
            result = export_to_airtable(records)
            
            # Also export to CSV
            csv_path = export_to_csv(records)
            
            print("\n✅ Test complete!")
            print(f"Airtable: {result['success']}/{result['total']} records synced")
            print(f"CSV: {csv_path}")
            
        except Exception as e:
            print(f"\n❌ Error during test: {str(e)}")
    else:
        print("\n⚠️ Please configure Airtable before running a test export.")
