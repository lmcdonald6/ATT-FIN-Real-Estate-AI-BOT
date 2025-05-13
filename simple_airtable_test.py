"""Simple Airtable Connection Test

This script tests the connection to Airtable using a Personal Access Token.
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables from .env file
load_dotenv()

# Airtable API configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

# Fix for URL-encoded table name in .env
if "%20" in TABLE_NAME:
    TABLE_NAME = TABLE_NAME.replace("%20", " ")

# Headers for API requests with Personal Access Token
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def test_connection():
    """Test the connection to Airtable."""
    print("[*] Testing Airtable connection...")
    print(f"[*] Using API key: {API_KEY[:5]}...{API_KEY[-5:]}")
    print(f"[*] Base ID: {BASE_ID}")
    print(f"[*] Table Name: {TABLE_NAME}")
    
    # Construct the URL for listing records
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    
    try:
        # Try to list records (limit to 1 to minimize data transfer)
        response = requests.get(f"{url}?maxRecords=1", headers=HEADERS)
        
        # Print response details
        print(f"[*] Response status: {response.status_code}")
        print(f"[*] Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            # Success!
            data = response.json()
            record_count = len(data.get('records', []))
            print(f"[+] Connection successful! Found {record_count} record(s).")
            
            # Print sample record if available
            if record_count > 0:
                print("[*] Sample record:")
                print(json.dumps(data['records'][0], indent=2))
                
            return True
        else:
            # Error
            print("[-] Connection failed. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text[:200])
            
            return False
    
    except Exception as e:
        print(f"[-] Error testing connection: {str(e)}")
        return False

def create_test_record():
    """Create a test record in Airtable."""
    if not test_connection():
        print("[-] Connection test failed. Skipping record creation.")
        return False
    
    # Create a simple test record
    test_record = {
        "Region": "Test Region",
        "Final Score": 75.0,
        "Market Phase": "Test Phase",
        "Risk Level": "Low",
        "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Construct the URL for creating a record
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    
    try:
        # Create the record
        print("\n[*] Creating test record...")
        payload = {"fields": test_record}
        response = requests.post(url, json=payload, headers=HEADERS)
        
        # Print response details
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            # Success!
            data = response.json()
            print("[+] Test record created successfully!")
            print("[*] Created record:")
            print(json.dumps(data, indent=2))
            return True
        else:
            # Error
            print("[-] Failed to create test record. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text[:200])
            return False
    
    except Exception as e:
        print(f"[-] Error creating test record: {str(e)}")
        return False

if __name__ == "__main__":
    print("[*] Simple Airtable Connection Test")
    print("--------------------------------------------------")
    
    # First test the connection
    connection_ok = test_connection()
    
    if connection_ok:
        # Ask if user wants to create a test record
        create_record = input("\nDo you want to create a test record? (y/n): ")
        if create_record.lower() == 'y':
            create_test_record()
        else:
            print("[*] Skipping test record creation.")
    else:
        print("\n[!] Please update your Airtable configuration in the .env file.")
        print("[!] Run the update_airtable_config.py script to update your configuration.")
