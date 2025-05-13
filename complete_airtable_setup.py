"""Complete Airtable Setup Script

This script creates the remaining fields in your Airtable base.
"""

import os
import requests
import json
from dotenv import load_dotenv
from typing import Dict, Any, List
import time

# Load environment variables
load_dotenv()

# Airtable API configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "Market Analysis")
TABLE_ID = os.getenv("AIRTABLE_TABLE_ID", "tbl9U6zb4wv6SVNs0")

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Remaining fields to create with fixed options
FIELDS_TO_CREATE = [
    {"name": "MonthlySales", "type": "number", "options": {"precision": 0}},
    {"name": "PropertyValue", "type": "number", "options": {"precision": 0}},
    {"name": "MonthlyRent", "type": "number", "options": {"precision": 0}},
    {"name": "AnnualIncome", "type": "number", "options": {"precision": 0}}
]

# Sample record data
SAMPLE_RECORD = {
    "Region": "Atlanta",
    "Score": 78.5,
    "Phase": "Growth",
    "Risk": "Moderate",
    "TrendScore": 82.3,
    "EconomicScore": 75.6,
    "PTRRatio": 11.45,
    "CapRate": 6.8,
    "MonthlySales": 1250,
    "Inventory": "Medium",
    "AvgAppreciation": 4.2,
    "PropertyValue": 330000,
    "MonthlyRent": 2400,
    "AnnualIncome": 85000,
    "Notes": "Sample record created by setup script"
}

def create_field(table_id: str, field_config: Dict[str, Any]) -> bool:
    """Create a new field in the table."""
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables/{table_id}/fields"
    
    try:
        response = requests.post(url, headers=HEADERS, json=field_config)
        response.raise_for_status()
        
        print(f"Created field: {field_config['name']}")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"Error creating field {field_config['name']}: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def create_record(table_id: str, record_data: Dict[str, Any]) -> bool:
    """Create a new record in the table."""
    url = f"https://api.airtable.com/v0/{BASE_ID}/{table_id}"
    
    payload = {
        "fields": record_data
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        record_id = response.json().get("id")
        print(f"Created record with ID: {record_id}")
        return True
    
    except requests.exceptions.RequestException as e:
        print(f"Error creating record: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return False

def complete_setup():
    """Complete the Airtable setup by creating remaining fields."""
    print("\nCompleting Market Analysis Table Setup")
    print("--------------------------------------------------")
    
    # Check API key
    if not API_KEY:
        print("Error: AIRTABLE_API_KEY not set in .env file")
        return
    
    # Check base ID
    if not BASE_ID:
        print("Error: AIRTABLE_BASE_ID not set in .env file")
        return
    
    # Create remaining fields
    print("\n### Creating remaining fields...")
    created_count = 0
    
    for field_config in FIELDS_TO_CREATE:
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
        
        if create_field(TABLE_ID, field_config):
            print(f"- Created field '{field_config['name']}' ({field_config['type']}).")
            created_count += 1
        else:
            print(f"- Failed to create field '{field_config['name']}'.")
    
    # Summary
    print("\n### Summary")
    print(f"- Created {created_count} new fields")
    print(f"- Total fields attempted: {len(FIELDS_TO_CREATE)}")
    
    if created_count == len(FIELDS_TO_CREATE):
        print("\nSetup complete! Your Market Analysis table now has all the required fields.")
        
        # Ask if user wants to create a sample record
        create_sample = input("\nDo you want to create a sample record? (y/n): ").lower() == 'y'
        
        if create_sample:
            print("\n### Creating sample record...")
            if create_record(TABLE_ID, SAMPLE_RECORD):
                print("- Created sample record successfully.")
            else:
                print("- Failed to create sample record.")
    else:
        print("\nSetup incomplete. Some fields could not be created.")
    
    # Next steps
    print("\n### Next Steps")
    print("1. Update your .env file with the following values:")
    print("```")
    print(f"AIRTABLE_BASE_ID={BASE_ID}")
    print(f"AIRTABLE_TABLE_ID={TABLE_ID}")
    print("USE_AIRTABLE=true")
    print("```")
    print("2. Make sure your API key is also set in the .env file.")
    print("3. Update your airtable_sync.py module with the field mappings from airtable_integration_code.py")

if __name__ == "__main__":
    complete_setup()
