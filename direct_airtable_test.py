"""Direct Airtable API Test

This script tests direct access to Airtable using the REST API v0 format.
"""

import os
import json
import requests
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Get the new token
API_TOKEN = os.getenv("AIRTABLE_API_KEY")

# Headers with the personal access token
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

def test_real_estate_base():
    """Test access to the Real Estate API Tracker base."""
    print("\n[*] Testing access to Real Estate API Tracker base...")
    
    # Try a few common base IDs that might be associated with Real Estate API Tracker
    # The base ID format is typically 'appXXXXXXXXXXXXXX'
    test_base_ids = [
        "app0T00hhThd6Qzym",  # Current configured base ID
        "appRealEstateTracker",  # A possible name-based ID
        "appRealEstate",  # Another possible name-based ID
    ]
    
    # Ask the user for the base ID
    user_base_id = input("Enter the base ID for your Real Estate API Tracker (or press Enter to try defaults): ").strip()
    if user_base_id:
        test_base_ids.insert(0, user_base_id)
    
    # Try each base ID
    for base_id in test_base_ids:
        print(f"\n[*] Testing base ID: {base_id}")
        
        # Try to list tables in this base
        url = f"https://api.airtable.com/v0/{base_id}"
        
        try:
            # First, try to access the base metadata
            meta_url = f"https://api.airtable.com/v0/meta/bases/{base_id}"
            meta_response = requests.get(meta_url, headers=HEADERS)
            
            print(f"[*] Metadata response status: {meta_response.status_code}")
            
            if meta_response.status_code == 200:
                print("[+] Successfully accessed base metadata!")
                meta_data = meta_response.json()
                print(f"[*] Base name: {meta_data.get('name', 'Unknown')}")
                
                # Try to list tables
                tables_url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
                tables_response = requests.get(tables_url, headers=HEADERS)
                
                if tables_response.status_code == 200:
                    tables = tables_response.json().get('tables', [])
                    print(f"[+] Found {len(tables)} tables in base:")
                    
                    for table in tables:
                        table_id = table.get('id')
                        table_name = table.get('name')
                        print(f"    * {table_name} (ID: {table_id})")
                        
                        # Try to access this table
                        test_table_access(base_id, table_name)
                else:
                    print(f"[-] Failed to list tables. Status: {tables_response.status_code}")
            else:
                # Try direct access to common table names
                print("[-] Failed to access base metadata. Trying direct table access...")
                test_table_names = [
                    "Market Analysis",
                    "Properties",
                    "Investments",
                    "Markets",
                    "Analysis"
                ]
                
                for table_name in test_table_names:
                    test_table_access(base_id, table_name)
        
        except Exception as e:
            print(f"[-] Error testing base ID {base_id}: {str(e)}")

def test_table_access(base_id, table_name):
    """Test access to a specific table in a base."""
    print(f"\n[*] Testing access to table: {table_name} in base: {base_id}")
    
    # URL-encode the table name
    import urllib.parse
    encoded_table_name = urllib.parse.quote(table_name)
    
    # Construct the URL
    url = f"https://api.airtable.com/v0/{base_id}/{encoded_table_name}"
    
    try:
        # Try to list records (limit to 1 to minimize data transfer)
        response = requests.get(f"{url}?maxRecords=1", headers=HEADERS)
        
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code == 200:
            # Success!
            data = response.json()
            record_count = len(data.get('records', []))
            print(f"[+] Successfully accessed table! Found {record_count} record(s).")
            
            # Update the .env file with this successful configuration
            update_env_file(base_id, table_name)
            
            # Ask if user wants to create a test record
            create_record = input(f"\nDo you want to create a test record in {table_name}? (y/n): ")
            if create_record.lower() == 'y':
                create_test_record(base_id, table_name)
            
            return True
        else:
            # Error
            print(f"[-] Failed to access table. Response status: {response.status_code}")
            try:
                error_data = response.json()
                print(f"    Error: {error_data}")
            except:
                print(f"    Response: {response.text[:100]}")
            
            return False
    
    except Exception as e:
        print(f"[-] Error testing table access: {str(e)}")
        return False

def create_test_record(base_id, table_name):
    """Create a test record in the specified table."""
    print(f"\n[*] Creating test record in {table_name}...")
    
    # URL-encode the table name
    import urllib.parse
    encoded_table_name = urllib.parse.quote(table_name)
    
    # Construct the URL
    url = f"https://api.airtable.com/v0/{base_id}/{encoded_table_name}"
    
    # Create a simple test record
    # Adjust fields based on the table structure
    test_record = {
        "fields": {
            "Region": "Test Region",
            "Final Score": 75.0,
            "Market Phase": "Test Phase",
            "Risk Level": "Low",
            "Timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    }
    
    try:
        # Create the record
        response = requests.post(url, json=test_record, headers=HEADERS)
        
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            # Success!
            data = response.json()
            print("[+] Test record created successfully!")
            print(f"[*] Record ID: {data.get('id', 'Unknown')}")
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

def update_env_file(base_id, table_name):
    """Update the .env file with successful configuration."""
    print(f"\n[*] Updating .env file with successful configuration...")
    print(f"[*] Base ID: {base_id}")
    print(f"[*] Table Name: {table_name}")
    
    # Read the current .env file
    env_path = ".env"
    try:
        with open(env_path, "r") as env_file:
            env_content = env_file.read()
    except FileNotFoundError:
        env_content = ""
    
    # Update the base ID and table name
    import re
    
    if "AIRTABLE_BASE_ID" in env_content:
        env_content = re.sub(r'AIRTABLE_BASE_ID=.*', f'AIRTABLE_BASE_ID={base_id}', env_content)
    else:
        env_content += f"\nAIRTABLE_BASE_ID={base_id}"
    
    if "AIRTABLE_TABLE_NAME" in env_content:
        env_content = re.sub(r'AIRTABLE_TABLE_NAME=.*', f'AIRTABLE_TABLE_NAME={table_name}', env_content)
    else:
        env_content += f"\nAIRTABLE_TABLE_NAME={table_name}"
    
    # Ensure USE_AIRTABLE is set to true
    if "USE_AIRTABLE" in env_content:
        env_content = re.sub(r'USE_AIRTABLE=.*', 'USE_AIRTABLE=true', env_content)
    else:
        env_content += "\nUSE_AIRTABLE=true"
    
    # Write the updated content back to the .env file
    with open(env_path, "w") as env_file:
        env_file.write(env_content)
    
    print("[+] .env file updated successfully!")

if __name__ == "__main__":
    print("[*] Direct Airtable API Test")
    print("--------------------------------------------------")
    print(f"[*] Using API token: {API_TOKEN[:5]}...{API_TOKEN[-5:]}")
    
    # Test access to the Real Estate API Tracker base
    test_real_estate_base()
