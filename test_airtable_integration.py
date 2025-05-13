"""Test Airtable Integration

This script tests the Airtable integration with the updated field mappings.
"""

import os
import json
from dotenv import load_dotenv
from datetime import datetime

# Import the airtable_sync module
from src.modules.airtable_sync import sync_record, find_record_by_region, map_fields, FIELD_MAPPINGS

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
    
    print("\n[*] Field mappings:")
    for app_field, airtable_field in FIELD_MAPPINGS.items():
        print(f"  {app_field} -> {airtable_field}")

def test_sync_record():
    """Test syncing a record to Airtable."""
    print("\n[*] Testing sync_record function...")
    
    # Create a sample record
    record_data = {
        "Region": "Dallas",  # Using a different region to avoid duplicates
        "Final Score": 82.1,
        "Market Phase": "Expansion",
        "Risk Level": "Low",
        "Trend Score": 85.7,
        "Economic Score": 79.2,
        "PTR Ratio": 12.3,
        "Cap Rate": 5.9,
        "Monthly Sales": 1450,
        "Inventory Level": "Low",
        "Avg Appreciation": 5.1,
        "Property Value": 380000,
        "Monthly Rent": 2800,
        "Annual Income": 92000
    }
    
    # Sync the record
    response = sync_record(record_data)
    
    print("\n[*] Airtable API Response:")
    print(json.dumps(response, indent=2))

def test_find_record():
    """Test finding a record by region."""
    print("\n[*] Testing find_record_by_region function...")
    
    # Find a record by region
    region = "Dallas"  # Match the region we just created
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
