"""Create Sample Record in Airtable

This script creates a sample record in the Market Analysis table.
"""

import os
import requests
import json
from dotenv import load_dotenv
from typing import Dict, Any

# Load environment variables
load_dotenv()

# Airtable API configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_ID = os.getenv("AIRTABLE_TABLE_ID", "tbl9U6zb4wv6SVNs0")

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

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

def create_record():
    """Create a sample record in the Market Analysis table."""
    print("Creating sample record in Airtable...")
    
    # Check API key and Base ID
    if not API_KEY or not BASE_ID or not TABLE_ID:
        print("Error: Missing Airtable configuration. Check your .env file.")
        return False
    
    # Airtable API endpoint
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    
    # Prepare data for Airtable API
    payload = {
        "fields": SAMPLE_RECORD
    }
    
    try:
        # Create a new record
        print(f"Sending POST request to {url}")
        response = requests.post(url, json=payload, headers=HEADERS)
        
        # Handle different status codes
        if response.status_code == 200 or response.status_code == 201:
            record_id = response.json().get("id")
            print(f"Success! Created record with ID: {record_id}")
            return True
        else:
            # Try to get error details from response
            try:
                error_data = response.json()
                print(f"Error creating record: {error_data}")
            except ValueError:
                print(f"Error creating record: {response.text}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"Request exception: {str(e)}")
        return False

if __name__ == "__main__":
    create_record()
