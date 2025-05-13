"""Airtable Sync Module

This module handles synchronization of market analysis data with Airtable.
It provides functions to create, update, and retrieve records from Airtable.
"""

import os
import requests
import json
import logging
from urllib.parse import quote
from dotenv import load_dotenv
from typing import Dict, Any, List, Optional
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('airtable_sync')

# Load environment variables
load_dotenv()

# Airtable API configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
TABLE_ID = os.getenv("AIRTABLE_TABLE_ID", "tbl9U6zb4wv6SVNs0")  # Default to the Market Analysis table ID
USE_AIRTABLE = os.getenv("USE_AIRTABLE", "false").lower() == "true"

# Fix for URL-encoded table name in .env
if TABLE_NAME and "%20" in TABLE_NAME:
    TABLE_NAME = TABLE_NAME.replace("%20", " ")
    logger.info(f"Decoded TABLE_NAME from URL encoding: {TABLE_NAME}")

# Determine which identifier to use for the table (name or ID)
TABLE_IDENTIFIER = TABLE_ID

# URL encode the table identifier for API requests
TABLE_IDENTIFIER_ENCODED = quote(TABLE_IDENTIFIER) if TABLE_IDENTIFIER else ""

# Airtable API endpoints
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_IDENTIFIER_ENCODED}" if BASE_ID and TABLE_IDENTIFIER_ENCODED else ""

# Log configuration
logger.info(f"Airtable Configuration:")
logger.info(f"  API Key: {API_KEY[:5]}...{API_KEY[-5:] if API_KEY else 'Not set'}")
logger.info(f"  Base ID: {BASE_ID}")
logger.info(f"  Table Name: {TABLE_NAME}")
logger.info(f"  Table ID: {TABLE_ID}")
logger.info(f"  Table Identifier Used: {TABLE_IDENTIFIER}")
logger.info(f"  Use Airtable: {USE_AIRTABLE}")
logger.info(f"  Base URL: {BASE_URL}")

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
    "Content-Type": "application/json"
}

# Field mappings for Airtable
# These map your application field names to Airtable field names
FIELD_MAPPINGS = {
    "Region": "Region",
    "Final Score": "Score",
    "Market Phase": "Phase",
    "Risk Level": "Risk",
    "Trend Score": "TrendScore",
    "Economic Score": "EconomicScore",
    "PTR Ratio": "PTRRatio",
    "Cap Rate": "CapRate",
    "Monthly Sales": "MonthlySales",
    "Inventory Level": "Inventory",
    "Avg Appreciation": "AvgAppreciation",
    "Property Value": "PropertyValue",
    "Monthly Rent": "MonthlyRent",
    "Annual Income": "AnnualIncome",
    "Timestamp": "Notes",  # We'll use Notes to store timestamp if needed
}

def map_fields(record_data):
    """Map field names from application to Airtable field names."""
    mapped_data = {}
    for key, value in record_data.items():
        if key in FIELD_MAPPINGS:
            mapped_key = FIELD_MAPPINGS[key]
            mapped_data[mapped_key] = value
        else:
            # Keep fields that don't have a mapping
            mapped_data[key] = value
    
    return mapped_data

def sync_record(record_data: Dict[str, Any]) -> Dict[str, Any]:
    """Sync a record with Airtable.
    
    This function will create a new record in Airtable with the provided data.
    
    Args:
        record_data: Dictionary containing the record data to be synced
        
    Returns:
        Dictionary containing the Airtable API response
    """
    if not USE_AIRTABLE:
        logger.warning("Airtable integration is disabled. Set USE_AIRTABLE=true in .env to enable.")
        return {"status": "skipped", "message": "Airtable integration is disabled"}
    
    if not API_KEY or not BASE_ID or not TABLE_IDENTIFIER:
        logger.error("Missing Airtable configuration. Check your .env file.")
        return {"status": "error", "message": "Missing Airtable configuration"}
    
    # Add timestamp to record
    record_data["Timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Map field names to Airtable field names
    mapped_record_data = map_fields(record_data)
    
    # Prepare data for Airtable API
    payload = {
        "fields": mapped_record_data
    }
    
    logger.info(f"Syncing record to Airtable: {record_data.get('Region', 'Unknown region')}")
    logger.debug(f"Original record data: {json.dumps(record_data, indent=2)}")
    logger.debug(f"Mapped record data: {json.dumps(mapped_record_data, indent=2)}")
    
    try:
        # Create a new record
        logger.debug(f"POST request to {BASE_URL}")
        response = requests.post(BASE_URL, json=payload, headers=HEADERS)
        
        # Log response details
        logger.debug(f"Response status code: {response.status_code}")
        logger.debug(f"Response headers: {dict(response.headers)}")
        
        # Handle different status codes
        if response.status_code == 200 or response.status_code == 201:
            logger.info(f"Successfully synced record to Airtable")
            return response.json()
        else:
            # Try to get error details from response
            try:
                error_data = response.json()
                logger.error(f"Error syncing record to Airtable: {error_data}")
                return {"status": "error", "message": str(error_data)}
            except ValueError:
                logger.error(f"Error syncing record to Airtable: {response.text}")
                return {"status": "error", "message": response.text}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception syncing record to Airtable: {str(e)}")
        
        # Try to get more details from the exception
        error_details = {}
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
            except ValueError:
                error_details = {"text": e.response.text[:200]}
        
        return {"status": "error", "message": str(e), "details": error_details}

def get_records(max_records: int = 100) -> List[Dict[str, Any]]:
    """Get records from Airtable.
    
    Args:
        max_records: Maximum number of records to retrieve
        
    Returns:
        List of dictionaries containing the records
    """
    if not USE_AIRTABLE:
        logger.warning("Airtable integration is disabled. Set USE_AIRTABLE=true in .env to enable.")
        return []
    
    if not API_KEY or not BASE_ID or not TABLE_IDENTIFIER:
        logger.error("Missing Airtable configuration. Check your .env file.")
        return []
    
    params = {
        "maxRecords": max_records,
        "view": "Grid view"
    }
    
    logger.info(f"Retrieving up to {max_records} records from Airtable")
    
    try:
        logger.debug(f"GET request to {BASE_URL}")
        response = requests.get(BASE_URL, params=params, headers=HEADERS)
        
        # Log response details
        logger.debug(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            # Extract records from response
            data = response.json()
            records = []
            
            for record in data.get("records", []):
                records.append({
                    "id": record.get("id"),
                    **record.get("fields", {})
                })
            
            logger.info(f"Retrieved {len(records)} records from Airtable")
            return records
        else:
            # Try to get error details from response
            try:
                error_data = response.json()
                logger.error(f"Error retrieving records from Airtable: {error_data}")
            except ValueError:
                logger.error(f"Error retrieving records from Airtable: {response.text}")
            return []
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception retrieving records from Airtable: {str(e)}")
        return []

def update_record(record_id: str, record_data: Dict[str, Any]) -> Dict[str, Any]:
    """Update an existing record in Airtable.
    
    Args:
        record_id: ID of the record to update
        record_data: Dictionary containing the updated record data
        
    Returns:
        Dictionary containing the Airtable API response
    """
    if not USE_AIRTABLE:
        logger.warning("Airtable integration is disabled. Set USE_AIRTABLE=true in .env to enable.")
        return {"status": "skipped", "message": "Airtable integration is disabled"}
    
    if not API_KEY or not BASE_ID or not TABLE_IDENTIFIER:
        logger.error("Missing Airtable configuration. Check your .env file.")
        return {"status": "error", "message": "Missing Airtable configuration"}
    
    if not record_id:
        logger.error("Missing record ID for update operation")
        return {"status": "error", "message": "Missing record ID"}
    
    # Add timestamp to record
    record_data["Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Prepare data for Airtable API
    payload = {
        "fields": record_data
    }
    
    logger.info(f"Updating record {record_id} in Airtable: {record_data.get('Region', 'Unknown region')}")
    
    try:
        # Update the record
        update_url = f"{BASE_URL}/{record_id}"
        logger.debug(f"PATCH request to {update_url}")
        response = requests.patch(update_url, json=payload, headers=HEADERS)
        
        # Log response details
        logger.debug(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            logger.info(f"Successfully updated record {record_id} in Airtable")
            return response.json()
        else:
            # Try to get error details from response
            try:
                error_data = response.json()
                logger.error(f"Error updating record in Airtable: {error_data}")
                return {"status": "error", "message": str(error_data)}
            except ValueError:
                logger.error(f"Error updating record in Airtable: {response.text}")
                return {"status": "error", "message": response.text}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception updating record in Airtable: {str(e)}")
        return {"status": "error", "message": str(e)}

def delete_record(record_id: str) -> Dict[str, Any]:
    """Delete a record from Airtable.
    
    Args:
        record_id: ID of the record to delete
        
    Returns:
        Dictionary containing the Airtable API response
    """
    if not USE_AIRTABLE:
        logger.warning("Airtable integration is disabled. Set USE_AIRTABLE=true in .env to enable.")
        return {"status": "skipped", "message": "Airtable integration is disabled"}
    
    if not API_KEY or not BASE_ID or not TABLE_IDENTIFIER:
        logger.error("Missing Airtable configuration. Check your .env file.")
        return {"status": "error", "message": "Missing Airtable configuration"}
    
    if not record_id:
        logger.error("Missing record ID for delete operation")
        return {"status": "error", "message": "Missing record ID"}
    
    logger.info(f"Deleting record {record_id} from Airtable")
    
    try:
        # Delete the record
        delete_url = f"{BASE_URL}/{record_id}"
        logger.debug(f"DELETE request to {delete_url}")
        response = requests.delete(delete_url, headers=HEADERS)
        
        # Log response details
        logger.debug(f"Response status code: {response.status_code}")
        
        if response.status_code == 200:
            logger.info(f"Successfully deleted record {record_id} from Airtable")
            return response.json()
        else:
            # Try to get error details from response
            try:
                error_data = response.json()
                logger.error(f"Error deleting record from Airtable: {error_data}")
                return {"status": "error", "message": str(error_data)}
            except ValueError:
                logger.error(f"Error deleting record from Airtable: {response.text}")
                return {"status": "error", "message": response.text}
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception deleting record from Airtable: {str(e)}")
        return {"status": "error", "message": str(e)}

def find_record_by_region(region: str) -> Optional[Dict[str, Any]]:
    """Find a record by region name.
    
    Args:
        region: Name of the region to search for
        
    Returns:
        Dictionary containing the record if found, None otherwise
    """
    if not USE_AIRTABLE:
        logger.warning("Airtable integration is disabled. Set USE_AIRTABLE=true in .env to enable.")
        return None
    
    if not API_KEY or not BASE_ID or not TABLE_IDENTIFIER:
        logger.error("Missing Airtable configuration. Check your .env file.")
        return None
    
    if not region:
        logger.error("Missing region name for search operation")
        return None
    
    logger.info(f"Searching for record with region: {region}")
    
    # Get the Airtable field name for Region
    region_field = FIELD_MAPPINGS.get("Region", "Region")
    
    # Try to use Airtable formula to filter records (more efficient)
    try:
        filter_formula = f"{{{region_field}}} = '{region}'"
        params = {
            "filterByFormula": filter_formula,
            "maxRecords": 1
        }
        
        logger.debug(f"GET request to {BASE_URL} with filter: {filter_formula}")
        response = requests.get(BASE_URL, params=params, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            records = data.get("records", [])
            
            if records:
                record = records[0]
                logger.info(f"Found record for region {region}")
                
                # Convert Airtable field names back to application field names
                fields = record.get("fields", {})
                reverse_mapped_fields = {}
                
                # Create a reverse mapping (Airtable field -> app field)
                reverse_mapping = {v: k for k, v in FIELD_MAPPINGS.items()}
                
                for field_name, field_value in fields.items():
                    if field_name in reverse_mapping:
                        app_field_name = reverse_mapping[field_name]
                        reverse_mapped_fields[app_field_name] = field_value
                    else:
                        reverse_mapped_fields[field_name] = field_value
                
                return {
                    "id": record.get("id"),
                    **reverse_mapped_fields
                }
            else:
                logger.info(f"No record found for region {region}")
                return None
        else:
            # Fallback to getting all records and filtering manually
            logger.warning(f"Filter query failed, falling back to manual search. Status: {response.status_code}")
    except Exception as e:
        logger.error(f"Error using filter query: {str(e)}")
        logger.warning("Falling back to manual search")
    
    # Get all records and filter manually
    records = get_records()
    
    # Find record with matching region
    for record in records:
        if record.get("Region") == region:
            logger.info(f"Found record for region {region} (manual search)")
            return record
    
    logger.info(f"No record found for region {region} (manual search)")
    return None
