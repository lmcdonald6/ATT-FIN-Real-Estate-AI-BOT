"""Airtable Sync Module for Data Scraping Service

This module provides functions to sync scraped real estate data with Airtable.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, List, Optional

# Add the parent directory to the path to import modules from the main project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the airtable_sync module from the main project
from src.modules.airtable_sync import sync_record, get_records, find_record_by_region

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('airtable_sync')

class AirtableSync:
    """Class for syncing scraped real estate data with Airtable."""
    
    def __init__(self):
        """Initialize the Airtable sync module."""
        self.logger = logging.getLogger('airtable_sync')
    
    def sync_properties(self, properties: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Sync properties with Airtable.
        
        Args:
            properties: List of property data dictionaries in Airtable format
            
        Returns:
            List of sync results
        """
        self.logger.info(f"Syncing {len(properties)} properties with Airtable")
        
        sync_results = []
        
        for property_data in properties:
            # Check if the property already exists in Airtable
            region = property_data.get("Region", "")
            existing_record = None
            
            if region:
                existing_record = find_record_by_region(region)
            
            if existing_record:
                # Update the existing record
                self.logger.info(f"Updating existing record for {region}")
                
                # Merge the existing record with the new data
                merged_data = {**existing_record, **property_data}
                
                # Remove the id field as it's not needed for the update
                if "id" in merged_data:
                    record_id = merged_data.pop("id")
                    
                    # Sync the merged data
                    result = sync_record(merged_data)
                    result["action"] = "update"
                    sync_results.append(result)
                else:
                    self.logger.warning(f"Found existing record for {region} but no id field")
                    
                    # Sync as a new record
                    result = sync_record(property_data)
                    result["action"] = "create"
                    sync_results.append(result)
            else:
                # Create a new record
                self.logger.info(f"Creating new record for {region}")
                
                # Sync the property data
                result = sync_record(property_data)
                result["action"] = "create"
                sync_results.append(result)
        
        self.logger.info(f"Synced {len(sync_results)} properties with Airtable")
        return sync_results
    
    def get_existing_properties(self) -> List[Dict[str, Any]]:
        """Get existing properties from Airtable.
        
        Returns:
            List of existing property records
        """
        self.logger.info("Getting existing properties from Airtable")
        
        # Get records from Airtable
        records = get_records()
        
        self.logger.info(f"Found {len(records)} existing properties in Airtable")
        return records
