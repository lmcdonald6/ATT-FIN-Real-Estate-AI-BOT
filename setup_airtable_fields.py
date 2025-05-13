"""Airtable Setup Script

This script creates the necessary fields in your Airtable base using the Airtable API directly.
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
TABLE_ID = os.getenv("AIRTABLE_TABLE_ID", "")

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Fields to create
FIELDS_TO_CREATE = [
    {"name": "Region", "type": "singleLineText"},
    {"name": "Score", "type": "number", "options": {"precision": 1}},
    {"name": "Phase", "type": "singleLineText"},
    {"name": "Risk", "type": "singleLineText"},
    {"name": "TrendScore", "type": "number", "options": {"precision": 1}},
    {"name": "EconomicScore", "type": "number", "options": {"precision": 1}},
    {"name": "PTRRatio", "type": "number", "options": {"precision": 2}},
    {"name": "CapRate", "type": "number", "options": {"precision": 2}},
    {"name": "MonthlySales", "type": "number"},
    {"name": "Inventory", "type": "singleLineText"},
    {"name": "AvgAppreciation", "type": "number", "options": {"precision": 2}},
    {"name": "PropertyValue", "type": "number"},
    {"name": "MonthlyRent", "type": "number"},
    {"name": "AnnualIncome", "type": "number"},
    {"name": "Notes", "type": "multilineText"}
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

def get_table_id() -> str:
    """Get the table ID for the Market Analysis table."""
    if TABLE_ID:
        print(f"Using table ID from environment: {TABLE_ID}")
        return TABLE_ID
    
    print(f"Looking up table ID for '{TABLE_NAME}'...")
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        tables = response.json().get("tables", [])
        for table in tables:
            if table.get("name") == TABLE_NAME:
                table_id = table.get("id")
                print(f"Found table ID: {table_id}")
                return table_id
        
        print(f"Table '{TABLE_NAME}' not found. Available tables:")
        for table in tables:
            print(f"  - {table.get('name')} ({table.get('id')})")
        
        # If table doesn't exist, create it
        return create_table(TABLE_NAME)
    
    except requests.exceptions.RequestException as e:
        print(f"Error getting table ID: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return ""

def create_table(table_name: str) -> str:
    """Create a new table in the base."""
    print(f"Creating new table: {table_name}")
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    
    payload = {
        "name": table_name,
        "fields": [
            {"name": "Name", "type": "singleLineText"}
        ]
    }
    
    try:
        response = requests.post(url, headers=HEADERS, json=payload)
        response.raise_for_status()
        
        table_id = response.json().get("id")
        print(f"Created table with ID: {table_id}")
        return table_id
    
    except requests.exceptions.RequestException as e:
        print(f"Error creating table: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return ""

def get_existing_fields(table_id: str) -> List[str]:
    """Get the names of existing fields in the table."""
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables/{table_id}/fields"
    
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        
        fields = response.json().get("fields", [])
        field_names = [field.get("name") for field in fields]
        print(f"Existing fields: {field_names}")
        return field_names
    
    except requests.exceptions.RequestException as e:
        print(f"Error getting existing fields: {e}")
        if hasattr(e, 'response') and e.response is not None:
            print(f"Response: {e.response.text}")
        return []

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

def setup_airtable():
    """Set up the Airtable structure."""
    print("\nMarket Analysis Table Setup")
    print("--------------------------------------------------")
    
    # Check API key
    if not API_KEY:
        print("Error: AIRTABLE_API_KEY not set in .env file")
        return
    
    # Check base ID
    if not BASE_ID:
        print("Error: AIRTABLE_BASE_ID not set in .env file")
        return
    
    # Get table ID
    table_id = get_table_id()
    if not table_id:
        print("Error: Could not get or create table")
        return
    
    # Get existing fields
    existing_fields = get_existing_fields(table_id)
    
    # Create fields
    print("\n### Creating fields...")
    created_count = 0
    skipped_count = 0
    
    for field_config in FIELDS_TO_CREATE:
        if field_config["name"] in existing_fields:
            print(f"- Field '{field_config['name']}' already exists, skipping.")
            skipped_count += 1
            continue
        
        # Add a small delay to avoid rate limiting
        time.sleep(0.5)
        
        if create_field(table_id, field_config):
            print(f"- Created field '{field_config['name']}' ({field_config['type']}).")
            created_count += 1
        else:
            print(f"- Failed to create field '{field_config['name']}'.")
    
    # Summary
    print("\n### Summary")
    print(f"- Created {created_count} new fields")
    print(f"- Skipped {skipped_count} existing fields")
    print(f"- Total fields required: {len(FIELDS_TO_CREATE)}")
    
    if created_count + skipped_count == len(FIELDS_TO_CREATE):
        print("\nSetup complete! Your Market Analysis table now has all the required fields.")
        
        # Ask if user wants to create a sample record
        create_sample = input("\nDo you want to create a sample record? (y/n): ").lower() == 'y'
        
        if create_sample:
            print("\n### Creating sample record...")
            if create_record(table_id, SAMPLE_RECORD):
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
    print(f"AIRTABLE_TABLE_ID={table_id}")
    print("USE_AIRTABLE=true")
    print("```")
    print("2. Make sure your API key is also set in the .env file.")
    print("3. Update your airtable_sync.py module with the field mappings.")

if __name__ == "__main__":
    setup_airtable()
