"""Test Airtable Integration with Table ID

This script tests the Airtable integration using the table ID instead of the table name.
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

def test_table_access():
    """Test access to the Market Analysis table using the table ID."""
    print("[*] Testing access to Market Analysis table using table ID...")
    print(f"[*] API Key: {API_KEY[:5]}...{API_KEY[-5:]}")
    print(f"[*] Base ID: {BASE_ID}")
    print(f"[*] Table ID: {TABLE_ID}")
    
    # Construct the URL with the table ID
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    print(f"[*] URL: {url}")
    
    try:
        # Try to list records (limit to 1 to minimize data transfer)
        response = requests.get(f"{url}?maxRecords=1", headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        print(f"[*] Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            data = response.json()
            record_count = len(data.get('records', []))
            print(f"[+] Successfully accessed table! Found {record_count} record(s).")
            
            if record_count > 0:
                print("[*] Sample record:")
                print(json.dumps(data['records'][0], indent=2))
            
            return True
        else:
            print("[-] Failed to access table. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text)
            return False
    
    except Exception as e:
        print(f"[-] Error accessing table: {str(e)}")
        return False

def create_sample_record():
    """Create a sample record in the Market Analysis table."""
    print("\n[*] Creating sample record in Market Analysis table...")
    
    # Construct the URL with the table ID
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    
    # Create a sample record
    record_data = {
        "fields": {
            "Region": "Sample City",
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
        print(f"[*] Response headers: {dict(response.headers)}")
        
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

def update_env_file():
    """Update the .env file with the table ID."""
    print("\n[*] Updating .env file with table ID...")
    
    # Read the current .env file
    env_path = ".env"
    try:
        with open(env_path, "r") as env_file:
            env_content = env_file.read()
    except FileNotFoundError:
        env_content = ""
    
    # Add the table ID to the .env file
    import re
    
    if "AIRTABLE_TABLE_ID" in env_content:
        env_content = re.sub(r'AIRTABLE_TABLE_ID=.*', f'AIRTABLE_TABLE_ID={TABLE_ID}', env_content)
    else:
        env_content += f"\nAIRTABLE_TABLE_ID={TABLE_ID}"
    
    # Write the updated content back to the .env file
    with open(env_path, "w") as env_file:
        env_file.write(env_content)
    
    print("[+] .env file updated successfully!")

def main():
    print("[*] Airtable Integration Test with Table ID")
    print("--------------------------------------------------")
    
    # Test access to the Market Analysis table
    if test_table_access():
        print("\n[+] Table access successful!")
        
        # Update the .env file with the table ID
        update_env_file()
        
        # Ask if user wants to create a sample record
        create_record = input("\nDo you want to create a sample record? (y/n): ")
        if create_record.lower() == 'y':
            create_sample_record()
    else:
        print("\n[-] Table access failed.")
        print("[!] Please check your API token, base ID, and table ID.")

if __name__ == "__main__":
    main()
