"""Create Sample Record in Airtable

This script creates a sample market analysis record in the Airtable database.
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Airtable API configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_ID = "tbl9U6zb4wv6SVNs0"  # Market Analysis table ID

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def create_sample_record():
    """Create a sample record in the Market Analysis table."""
    print("[*] Creating sample record in Market Analysis table...")
    print(f"[*] API Key: {API_KEY[:5]}...{API_KEY[-5:]}")
    print(f"[*] Base ID: {BASE_ID}")
    print(f"[*] Table ID: {TABLE_ID}")
    
    # Construct the URL with the table ID
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    print(f"[*] URL: {url}")
    
    # Create a sample record
    record_data = {
        "fields": {
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
    }
    
    try:
        # Create the record
        response = requests.post(url, json=record_data, headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            record_id = data.get('id')
            print(f"[+] Sample record created successfully! ID: {record_id}")
            print("[*] Created record:")
            print(json.dumps(data, indent=2))
            return True
        else:
            print("[-] Failed to create sample record. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text)
            return False
    
    except Exception as e:
        print(f"[-] Error creating sample record: {str(e)}")
        return False

if __name__ == "__main__":
    print("[*] Airtable Sample Record Creation")
    print("--------------------------------------------------")
    
    # Create a sample record
    create_sample_record()
