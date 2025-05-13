"""Data Scraping Service Main Module

This module provides the main entry point for the data scraping service.
"""

import os
import sys
import json
import logging
import argparse
from typing import Dict, Any, List, Optional
from datetime import datetime

# Import service modules
from data_scraping_service.scrapers.zillow_scraper import ZillowScraper
from data_scraping_service.scrapers.realtor_scraper import RealtorScraper
from data_scraping_service.data_processor import DataProcessor
from data_scraping_service.airtable_sync import AirtableSync
from data_scraping_service.scheduler import TaskScheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), 'scraper.log'))
    ]
)
logger = logging.getLogger('data_scraping_service')

class DataScrapingService:
    """Main class for the data scraping service."""
    
    def __init__(self):
        """Initialize the data scraping service."""
        self.logger = logging.getLogger('data_scraping_service')
        self.zillow_scraper = ZillowScraper()
        self.realtor_scraper = RealtorScraper()
        self.data_processor = DataProcessor()
        self.airtable_sync = AirtableSync()
        self.scheduler = TaskScheduler()
        
        # Create data directory if it doesn't exist
        os.makedirs(os.path.join(os.path.dirname(__file__), 'data'), exist_ok=True)
    
    def scrape_properties(self, location: str, source: str = 'all', **kwargs) -> List[Dict[str, Any]]:
        """Scrape properties from the specified source(s).
        
        Args:
            location: Location to search in (city, state, zip code, etc.)
            source: Source to scrape from ('zillow', 'realtor', or 'all')
            **kwargs: Additional search parameters
            
        Returns:
            List of property data dictionaries
        """
        self.logger.info(f"Scraping properties in {location} from {source}")
        
        properties = []
        
        # Scrape from Zillow
        if source.lower() in ['zillow', 'all']:
            self.logger.info(f"Scraping properties from Zillow for {location}")
            try:
                zillow_properties = self.zillow_scraper.search_properties(location, **kwargs)
                self.logger.info(f"Found {len(zillow_properties)} properties on Zillow")
                properties.extend(zillow_properties)
            except Exception as e:
                self.logger.error(f"Error scraping properties from Zillow: {str(e)}")
        
        # Scrape from Realtor.com
        if source.lower() in ['realtor', 'all']:
            self.logger.info(f"Scraping properties from Realtor.com for {location}")
            try:
                realtor_properties = self.realtor_scraper.search_properties(location, **kwargs)
                self.logger.info(f"Found {len(realtor_properties)} properties on Realtor.com")
                properties.extend(realtor_properties)
            except Exception as e:
                self.logger.error(f"Error scraping properties from Realtor.com: {str(e)}")
        
        # Clean and process the properties
        if properties:
            self.logger.info(f"Processing {len(properties)} properties")
            try:
                # Clean the property data
                properties = self.data_processor.clean_property_data(properties)
                
                # Merge properties from different sources
                properties = self.data_processor.merge_property_data(properties)
                
                # Save the raw properties to a file
                self._save_to_json(properties, f"properties_{location.replace(' ', '_')}")
            except Exception as e:
                self.logger.error(f"Error processing properties: {str(e)}")
        
        return properties
    
    def scrape_market_data(self, location: str, source: str = 'all') -> Optional[Dict[str, Any]]:
        """Scrape market data for the specified location.
        
        Args:
            location: Location to get market data for (city, state, zip code, etc.)
            source: Source to scrape from ('zillow', 'realtor', or 'all')
            
        Returns:
            Market data dictionary or None if not found
        """
        self.logger.info(f"Scraping market data for {location} from {source}")
        
        market_data = None
        
        # Scrape from Zillow
        if source.lower() in ['zillow', 'all']:
            self.logger.info(f"Scraping market data from Zillow for {location}")
            try:
                zillow_market_data = self.zillow_scraper.get_market_data(location)
                if zillow_market_data:
                    self.logger.info(f"Found market data on Zillow for {location}")
                    market_data = zillow_market_data
            except Exception as e:
                self.logger.error(f"Error scraping market data from Zillow: {str(e)}")
        
        # Scrape from Realtor.com if we didn't get data from Zillow
        if (source.lower() in ['realtor', 'all']) and (market_data is None):
            self.logger.info(f"Scraping market data from Realtor.com for {location}")
            try:
                realtor_market_data = self.realtor_scraper.get_market_data(location)
                if realtor_market_data:
                    self.logger.info(f"Found market data on Realtor.com for {location}")
                    market_data = realtor_market_data
            except Exception as e:
                self.logger.error(f"Error scraping market data from Realtor.com: {str(e)}")
        
        # Clean and process the market data
        if market_data:
            self.logger.info(f"Processing market data for {location}")
            try:
                # Clean the market data
                market_data = self.data_processor.clean_market_data(market_data)
                
                # Save the market data to a file
                self._save_to_json(market_data, f"market_data_{location.replace(' ', '_')}")
            except Exception as e:
                self.logger.error(f"Error processing market data: {str(e)}")
        
        return market_data
    
    def sync_with_airtable(self, properties: List[Dict[str, Any]], market_data: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Sync properties and market data with Airtable.
        
        Args:
            properties: List of property data dictionaries
            market_data: Optional market data dictionary
            
        Returns:
            List of sync results
        """
        self.logger.info(f"Syncing {len(properties)} properties with Airtable")
        
        # Calculate derived metrics
        if market_data:
            properties = self.data_processor.calculate_derived_metrics(properties, market_data)
        else:
            properties = self.data_processor.calculate_derived_metrics(properties)
        
        # Convert to Airtable format
        airtable_properties = self.data_processor.convert_to_airtable_format(properties)
        
        # Sync with Airtable
        sync_results = self.airtable_sync.sync_properties(airtable_properties)
        
        self.logger.info(f"Synced {len(sync_results)} properties with Airtable")
        return sync_results
    
    def schedule_scraping_task(self, location: str, schedule_type: str, interval: int, 
                             source: str = 'all', **kwargs):
        """Schedule a scraping task for the specified location.
        
        Args:
            location: Location to search in (city, state, zip code, etc.)
            schedule_type: Type of schedule (daily, hourly, minutes)
            interval: Interval for the schedule
            source: Source to scrape from ('zillow', 'realtor', or 'all')
            **kwargs: Additional search parameters
        """
        self.logger.info(f"Scheduling scraping task for {location} to run {schedule_type} every {interval} interval")
        
        # Create a task function that scrapes properties and market data and syncs with Airtable
        def scraping_task():
            self.logger.info(f"Running scraping task for {location}")
            
            # Scrape properties
            properties = self.scrape_properties(location, source, **kwargs)
            
            # Scrape market data
            market_data = self.scrape_market_data(location, source)
            
            # Sync with Airtable
            if properties:
                self.sync_with_airtable(properties, market_data)
        
        # Add the task to the scheduler
        task_name = f"scrape_{location.replace(' ', '_')}"
        self.scheduler.add_task(task_name, scraping_task, schedule_type, interval)
    
    def start_scheduler(self):
        """Start the scheduler."""
        self.logger.info("Starting scheduler")
        self.scheduler.start()
    
    def stop_scheduler(self):
        """Stop the scheduler."""
        self.logger.info("Stopping scheduler")
        self.scheduler.stop()
    
    def _save_to_json(self, data: Any, filename: str) -> bool:
        """Save data to a JSON file.
        
        Args:
            data: Data to save
            filename: Name of the file to save to (without extension)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create the data directory if it doesn't exist
            data_dir = os.path.join(os.path.dirname(__file__), 'data')
            os.makedirs(data_dir, exist_ok=True)
            
            # Add a timestamp to the filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filepath = os.path.join(data_dir, f"{filename}_{timestamp}.json")
            
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, default=str)
            
            self.logger.info(f"Saved data to {filepath}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving data to {filename}: {str(e)}")
            return False

# Command-line interface
def main():
    """Main entry point for the data scraping service."""
    parser = argparse.ArgumentParser(description="Real Estate Data Scraping Service")
    parser.add_argument("--location", type=str, help="Location to search in (city, state, zip code, etc.)")
    parser.add_argument("--source", type=str, default="all", choices=["zillow", "realtor", "all"], help="Source to scrape from")
    parser.add_argument("--max-results", type=int, default=20, help="Maximum number of results to return")
    parser.add_argument("--min-price", type=int, help="Minimum price")
    parser.add_argument("--max-price", type=int, help="Maximum price")
    parser.add_argument("--min-beds", type=int, help="Minimum number of bedrooms")
    parser.add_argument("--min-baths", type=int, help="Minimum number of bathrooms")
    parser.add_argument("--property-type", type=str, help="Type of property")
    parser.add_argument("--schedule", type=str, choices=["daily", "hourly", "minutes"], help="Type of schedule")
    parser.add_argument("--interval", type=int, help="Interval for the schedule")
    parser.add_argument("--sync", action="store_true", help="Sync with Airtable")
    
    args = parser.parse_args()
    
    # Create the data scraping service
    service = DataScrapingService()
    
    # Check if we have a location
    if args.location:
        # Build search parameters
        search_params = {
            "max_results": args.max_results
        }
        
        if args.min_price:
            search_params["min_price"] = args.min_price
        
        if args.max_price:
            search_params["max_price"] = args.max_price
        
        if args.min_beds:
            search_params["min_beds"] = args.min_beds
        
        if args.min_baths:
            search_params["min_baths"] = args.min_baths
        
        if args.property_type:
            search_params["property_type"] = args.property_type
        
        # Scrape properties
        properties = service.scrape_properties(args.location, args.source, **search_params)
        
        # Scrape market data
        market_data = service.scrape_market_data(args.location, args.source)
        
        # Sync with Airtable if requested
        if args.sync and properties:
            service.sync_with_airtable(properties, market_data)
        
        # Schedule if requested
        if args.schedule and args.interval:
            service.schedule_scraping_task(args.location, args.schedule, args.interval, args.source, **search_params)
            service.start_scheduler()
            
            # Keep the script running
            try:
                while True:
                    import time
                    time.sleep(1)
            except KeyboardInterrupt:
                service.stop_scheduler()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
