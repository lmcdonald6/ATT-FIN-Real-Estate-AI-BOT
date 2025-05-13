"""Get Airtable Table Schema

This script retrieves the schema (field names and types) of the Market Analysis table.
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

def get_table_schema():
    """Get the schema of the Market Analysis table."""
    print("[*] Getting schema for Market Analysis table...")
    print(f"[*] API Key: {API_KEY[:5]}...{API_KEY[-5:]}")
    print(f"[*] Base ID: {BASE_ID}")
    print(f"[*] Table ID: {TABLE_ID}")
    
    # Construct the URL to get the table metadata
    url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables/{TABLE_ID}"
    print(f"[*] URL: {url}")
    
    try:
        # Get the table metadata
        response = requests.get(url, headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            fields = data.get('fields', [])
            
            print(f"[+] Found {len(fields)} fields in table:")
            for field in fields:
                field_id = field.get('id')
                field_name = field.get('name')
                field_type = field.get('type')
                print(f"    - {field_name} (Type: {field_type}, ID: {field_id})")
            
            return fields
        else:
            print("[-] Failed to get table schema. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text)
            return []
    
    except Exception as e:
        print(f"[-] Error getting table schema: {str(e)}")
        return []

def get_sample_record():
    """Get a sample record from the Market Analysis table."""
    print("\n[*] Getting sample record from Market Analysis table...")
    
    # Construct the URL to get records
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    print(f"[*] URL: {url}")
    
    try:
        # Get one record
        response = requests.get(f"{url}?maxRecords=1", headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            records = data.get('records', [])
            
            if records:
                record = records[0]
                print(f"[+] Found sample record (ID: {record.get('id')}):")
                print(json.dumps(record, indent=2))
                
                # Show the fields in the record
                fields = record.get('fields', {})
                print("\n[*] Fields in the record:")
                for field_name, field_value in fields.items():
                    print(f"    - {field_name}: {field_value}")
                
                return record
            else:
                print("[-] No records found in the table.")
                return None
        else:
            print("[-] Failed to get sample record. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text)
            return None
    
    except Exception as e:
        print(f"[-] Error getting sample record: {str(e)}")
        return None

if __name__ == "__main__":
    print("[*] Airtable Table Schema Retrieval")
    print("--------------------------------------------------")
    
    # Get the table schema
    fields = get_table_schema()
    
    # Get a sample record
    if fields:
        get_sample_record()
