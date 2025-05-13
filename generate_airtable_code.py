"""Generate Airtable Sync Code

This script generates code for the Airtable sync module that you can manually
copy and paste into your project. It includes field mappings and functions
to handle the conversion between your application's field names and Airtable's field names.
"""

import json
from datetime import datetime

# Define the field mappings
# These are the fields from your application and how they map to Airtable fields
FIELD_MAPPINGS = {
    # Your application field name -> Airtable field name
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

# Generate the field mappings code
def generate_field_mappings_code():
    code = """# Field mappings for Airtable
# These map your application field names to Airtable field names
FIELD_MAPPINGS = {
"""
    
    for app_field, airtable_field in FIELD_MAPPINGS.items():
        code += f"    \"{app_field}\": \"{airtable_field}\",\n"
    
    code += "}\n"
    return code

# Generate the map_fields function
def generate_map_fields_function():
    code = """def map_fields(record_data):
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
"""
    return code

# Generate the updated sync_record function
def generate_sync_record_function():
    code = """def sync_record(record_data: Dict[str, Any]) -> Dict[str, Any]:
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
    logger.debug(f"Record data: {json.dumps(mapped_record_data, indent=2)}")
    
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
"""
    return code

# Generate the updated find_record_by_region function
def generate_find_record_function():
    code = """def find_record_by_region(region: str) -> Optional[Dict[str, Any]]:
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
"""
    return code

# Generate a sample record for testing
def generate_sample_record():
    # Create a sample record with all the required fields
    record_data = {
        "Region": "Atlanta",
        "Final Score": 78.5,
        "Market Phase": "Growth",
        "Risk Level": "Moderate",
        "Trend Score": 82.3,
        "Economic Score": 75.6,
        "PTR Ratio": 11.45,
        "Cap Rate": 6.8,
        "Monthly Sales": 1250,
        "Inventory Level": "Medium",
        "Avg Appreciation": 4.2,
        "Property Value": 330000,
        "Monthly Rent": 2400,
        "Annual Income": 85000,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Map the fields
    mapped_data = {}
    for key, value in record_data.items():
        if key in FIELD_MAPPINGS:
            mapped_key = FIELD_MAPPINGS[key]
            mapped_data[mapped_key] = value
        else:
            mapped_data[key] = value
    
    return {
        "original": record_data,
        "mapped": mapped_data
    }

# Generate the complete code
def generate_complete_code():
    code = """"""Airtable Sync Module

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

"""
    
    # Add field mappings
    code += generate_field_mappings_code() + "\n"
    
    # Add Airtable API configuration
    code += """# Airtable API configuration
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

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}" if API_KEY else "",
    "Content-Type": "application/json"
}

# Log configuration
logger.info(f"Airtable Configuration:")
logger.info(f"  API Key: {API_KEY[:5]}...{API_KEY[-5:] if API_KEY else 'Not set'}")
logger.info(f"  Base ID: {BASE_ID}")
logger.info(f"  Table Name: {TABLE_NAME}")
logger.info(f"  Table ID: {TABLE_ID}")
logger.info(f"  Table Identifier Used: {TABLE_IDENTIFIER}")
logger.info(f"  Use Airtable: {USE_AIRTABLE}")
logger.info(f"  Base URL: {BASE_URL}")
"""
    
    # Add map_fields function
    code += generate_map_fields_function() + "\n"
    
    # Add sync_record function
    code += generate_sync_record_function() + "\n"
    
    # Add find_record_by_region function
    code += generate_find_record_function() + "\n"
    
    return code

# Generate a test script
def generate_test_script():
    code = """"""Test Airtable Integration

This script tests the Airtable integration with the updated field mappings.
"""

import os
import json
from dotenv import load_dotenv
from datetime import datetime

# Import the airtable_sync module
from src.modules.airtable_sync import sync_record, find_record_by_region, map_fields

# Load environment variables
load_dotenv()

def test_field_mapping():
    """Test the field mapping functionality."""    
    print("[*] Testing field mapping...")
    
    # Create a sample record
    record_data = {
        "Region": "Atlanta",
        "Final Score": 78.5,
        "Market Phase": "Growth",
        "Risk Level": "Moderate",
        "Trend Score": 82.3,
        "Economic Score": 75.6,
        "PTR Ratio": 11.45,
        "Cap Rate": 6.8,
        "Monthly Sales": 1250,
        "Inventory Level": "Medium",
        "Avg Appreciation": 4.2,
        "Property Value": 330000,
        "Monthly Rent": 2400,
        "Annual Income": 85000,
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Map the fields
    mapped_data = map_fields(record_data)
    
    print("\n[*] Original record data:")
    print(json.dumps(record_data, indent=2))
    
    print("\n[*] Mapped record data:")
    print(json.dumps(mapped_data, indent=2))

def test_sync_record():
    """Test syncing a record to Airtable."""    
    print("\n[*] Testing sync_record function...")
    
    # Create a sample record
    record_data = {
        "Region": "Atlanta",
        "Final Score": 78.5,
        "Market Phase": "Growth",
        "Risk Level": "Moderate",
        "Trend Score": 82.3,
        "Economic Score": 75.6,
        "PTR Ratio": 11.45,
        "Cap Rate": 6.8,
        "Monthly Sales": 1250,
        "Inventory Level": "Medium",
        "Avg Appreciation": 4.2,
        "Property Value": 330000,
        "Monthly Rent": 2400,
        "Annual Income": 85000
    }
    
    # Sync the record
    response = sync_record(record_data)
    
    print("\n[*] Airtable API Response:")
    print(json.dumps(response, indent=2))

def test_find_record():
    """Test finding a record by region."""    
    print("\n[*] Testing find_record_by_region function...")
    
    # Find a record by region
    region = "Atlanta"
    record = find_record_by_region(region)
    
    if record:
        print(f"\n[+] Found record for region {region}:")
        print(json.dumps(record, indent=2))
    else:
        print(f"\n[-] No record found for region {region}")

if __name__ == "__main__":
    print("[*] Airtable Integration Test")
    print("--------------------------------------------------")
    
    # Test field mapping
    test_field_mapping()
    
    # Test syncing a record
    test_sync_record()
    
    # Test finding a record
    test_find_record()
"""
    return code

# Generate instructions for manual integration
def generate_instructions():
    instructions = """# Airtable Integration Instructions

## Step 1: Update the airtable_sync.py Module

Replace the contents of the `src/modules/airtable_sync.py` file with the generated code.

## Step 2: Update the .env File

Make sure your .env file has the following variables:

```
AIRTABLE_API_KEY=your_api_key
AIRTABLE_BASE_ID=app0TO0hhThd6Qzym
AIRTABLE_TABLE_ID=tbl9U6zb4wv6SVNs0
USE_AIRTABLE=true
```

## Step 3: Create the Required Fields in Airtable

In your Airtable base, add the following fields to the Market Analysis table:

1. Region (Single line text)
2. Score (Number)
3. Phase (Single line text)
4. Risk (Single line text)
5. TrendScore (Number)
6. EconomicScore (Number)
7. PTRRatio (Number)
8. CapRate (Number)
9. MonthlySales (Number)
10. Inventory (Single line text)
11. AvgAppreciation (Number)
12. PropertyValue (Number)
13. MonthlyRent (Number)
14. AnnualIncome (Number)
15. Notes (Long text)

## Step 4: Test the Integration

Run the test script to verify that the integration is working correctly:

```bash
python test_airtable_integration.py
```

## Field Mappings

The following field mappings are used to convert between your application's field names and Airtable field names:

| Application Field | Airtable Field |
|-------------------|---------------|
| Region | Region |
| Final Score | Score |
| Market Phase | Phase |
| Risk Level | Risk |
| Trend Score | TrendScore |
| Economic Score | EconomicScore |
| PTR Ratio | PTRRatio |
| Cap Rate | CapRate |
| Monthly Sales | MonthlySales |
| Inventory Level | Inventory |
| Avg Appreciation | AvgAppreciation |
| Property Value | PropertyValue |
| Monthly Rent | MonthlyRent |
| Annual Income | AnnualIncome |
| Timestamp | Notes |
"""
    return instructions

# Main function
def main():
    # Generate the complete code
    code = generate_complete_code()
    
    # Generate the test script
    test_script = generate_test_script()
    
    # Generate instructions
    instructions = generate_instructions()
    
    # Generate a sample record
    sample_record = generate_sample_record()
    
    # Write the code to files
    with open("airtable_sync_code.py", "w") as f:
        f.write(code)
    
    with open("test_airtable_integration.py", "w") as f:
        f.write(test_script)
    
    with open("airtable_integration_instructions.md", "w") as f:
        f.write(instructions)
    
    # Print summary
    print("Generated files:")
    print("1. airtable_sync_code.py - Code for the airtable_sync.py module")
    print("2. test_airtable_integration.py - Test script for the Airtable integration")
    print("3. airtable_integration_instructions.md - Instructions for manual integration")
    
    print("\nSample Record:")
    print("Original:")
    print(json.dumps(sample_record["original"], indent=2))
    print("\nMapped:")
    print(json.dumps(sample_record["mapped"], indent=2))

if __name__ == "__main__":
    main()
