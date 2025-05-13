"""Query Airtable Table

This script queries the Airtable table to get information about its structure.
"""

import os
import json
import requests
from dotenv import load_dotenv

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

def query_table():
    """Query the table to get information about its structure."""
    print("[*] Querying Market Analysis table...")
    print(f"[*] API Key: {API_KEY[:5]}...{API_KEY[-5:]}")
    print(f"[*] Base ID: {BASE_ID}")
    print(f"[*] Table ID: {TABLE_ID}")
    
    # Construct the URL to get records
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    print(f"[*] URL: {url}")
    
    try:
        # Get records
        response = requests.get(url, headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            print(f"[+] Found {len(records)} records in table.")
            
            if records:
                # Get the fields from the first record
                first_record = records[0]
                fields = first_record.get('fields', {})
                
                print("\n[*] Fields in the table:")
                for field_name, field_value in fields.items():
                    print(f"    - {field_name}: {type(field_value).__name__}")
                
                print("\n[*] Sample record:")
                print(json.dumps(first_record, indent=2))
            
            return records
        else:
            print("[-] Failed to query table. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text)
            return []
    
    except Exception as e:
        print(f"[-] Error querying table: {str(e)}")
        return []

def create_sample_record():
    """Create a sample record in the Market Analysis table."""
    print("\n[*] Creating sample record in Market Analysis table...")
    
    # Construct the URL
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    
    # Create a sample record with minimal fields
    record_data = {
        "fields": {
            "Region": "Atlanta",
            "Score": 78.5,
            "Phase": "Growth",
            "Risk": "Moderate",
            "Notes": "Sample record created by API"
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
    print("[*] Airtable Table Query")
    print("--------------------------------------------------")
    
    # Query the table
    records = query_table()
    
    # Create a sample record if the query was successful
    if records:
        create_sample_record()
