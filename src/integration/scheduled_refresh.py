#!/usr/bin/env python3
"""
Scheduled Neighborhood Data Refresh

This script sets up a scheduler to periodically refresh neighborhood data
and export it to Airtable for tracking and visualization.
"""

import os
import sys
import time
import logging
from datetime import datetime
from typing import List, Dict, Any

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

try:
    import schedule
except ImportError:
    logger.error("Schedule package not installed. Run 'pip install schedule'")
    sys.exit(1)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

from src.integration.combine_market_and_sentiment import combine_analysis
from src.integration.airtable_exporter import export_to_airtable
from src.integration.leaderboard_simple import generate_leaderboard

# ZIP codes to analyze
ZIPS = ["30318", "11238", "90210", "33101", "60614", "75201"]


def daily_refresh(zip_codes: List[str] = None) -> Dict[str, Any]:
    """
    Perform a daily refresh of neighborhood data and export to Airtable.
    
    Args:
        zip_codes: List of ZIP codes to refresh (defaults to ZIPS)
        
    Returns:
        Dictionary with refresh results
    """
    if zip_codes is None:
        zip_codes = ZIPS
    
    logger.info(f"Starting scheduled neighborhood refresh for {len(zip_codes)} ZIP codes")
    print(f"\n⏰ Scheduled neighborhood refresh starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}...")
    print(f"Refreshing {len(zip_codes)} ZIP codes: {', '.join(zip_codes)}")
    
    # Analyze all ZIP codes
    results = []
    for zip_code in zip_codes:
        try:
            print(f"Analyzing ZIP {zip_code}...")
            result = combine_analysis(zip_code)
            results.append(result)
        except Exception as e:
            logger.error(f"Error analyzing ZIP {zip_code}: {str(e)}")
            print(f"❌ Error analyzing ZIP {zip_code}: {str(e)}")
    
    # Export to Airtable
    try:
        export_result = export_to_airtable(results)
        print(f"✅ Synced {export_result['success']}/{export_result['total']} records to Airtable")
    except Exception as e:
        logger.error(f"Error exporting to Airtable: {str(e)}")
        print(f"❌ Error exporting to Airtable: {str(e)}")
        export_result = {"success": 0, "total": len(results), "error": str(e)}
    
    # Generate leaderboard
    try:
        leaderboard_path = generate_leaderboard(zip_codes, sort_key="reputation_score", top_n=len(zip_codes))
        print(f"✅ Generated leaderboard at {leaderboard_path}")
    except Exception as e:
        logger.error(f"Error generating leaderboard: {str(e)}")
        print(f"❌ Error generating leaderboard: {str(e)}")
    
    logger.info(f"Completed scheduled refresh: {export_result['success']}/{export_result['total']} records synced")
    print(f"✅ Refresh completed at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return {
        "timestamp": datetime.now().isoformat(),
        "zip_codes": zip_codes,
        "analyzed": len(results),
        "synced": export_result.get("success", 0),
        "total": export_result.get("total", 0)
    }


def setup_schedule(refresh_time: str = "03:00", run_now: bool = False) -> None:
    """
    Set up the daily refresh schedule.
    
    Args:
        refresh_time: Time to run the daily refresh (24-hour format)
        run_now: Whether to run the refresh immediately
    """
    # Schedule the daily refresh
    schedule.every().day.at(refresh_time).do(daily_refresh)
    logger.info(f"Scheduled daily refresh at {refresh_time}")
    
    # Run immediately if requested
    if run_now:
        logger.info("Running initial refresh")
        daily_refresh()
    
    print(f"📅 Scheduler running. Daily refresh scheduled for {refresh_time}.")
    print("Press Ctrl+C to stop.")
    
    try:
        while True:
            schedule.run_pending()
            time.sleep(60)
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
        print("\n✅ Scheduler stopped.")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Scheduled neighborhood data refresh")
    parser.add_argument("--time", type=str, default="03:00", help="Time to run the daily refresh (24-hour format)")
    parser.add_argument("--run-now", action="store_true", help="Run the refresh immediately")
    parser.add_argument("--zip-codes", type=str, help="Comma-separated list of ZIP codes to refresh")
    
    args = parser.parse_args()
    
    # Override ZIP codes if provided
    if args.zip_codes:
        ZIPS = [z.strip() for z in args.zip_codes.split(",")]
    
    # Set up the schedule
    setup_schedule(args.time, args.run_now)
