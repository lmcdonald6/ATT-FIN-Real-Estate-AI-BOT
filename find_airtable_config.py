"""Find Airtable Configuration

This script automatically tries different base IDs and table names to find the correct configuration.
"""

import os
import json
import requests
import re
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the API token
API_TOKEN = os.getenv("AIRTABLE_API_KEY")

# Headers with the personal access token
HEADERS = {
    "Authorization": f"Bearer {API_TOKEN}",
    "Content-Type": "application/json"
}

# Possible base IDs to try
BASE_IDS = [
    "appRealEstateTracker",
    "appRealEstate",
    "app0T00hhThd6Qzym",  # Current configured base ID
    "appRealEstateAPITracker",
    "appRealEstateAPI",
    "appRETracker",
    "appREAPI"
]

# Possible table names to try
TABLE_NAMES = [
    "Market Analysis",
    "Properties",
    "Investments",
    "Markets",
    "Analysis",
    "Real Estate",
    "Property Analysis"
]

def test_base_and_table(base_id, table_name):
    """Test access to a specific table in a base."""
    print(f"[*] Testing base: {base_id}, table: {table_name}")
    
    # URL-encode the table name
    import urllib.parse
    encoded_table_name = urllib.parse.quote(table_name)
    
    # Construct the URL
    url = f"https://api.airtable.com/v0/{base_id}/{encoded_table_name}"
    
    try:
        # Try to list records (limit to 1 to minimize data transfer)
        response = requests.get(f"{url}?maxRecords=1", headers=HEADERS)
        
        if response.status_code == 200:
            # Success!
            data = response.json()
            record_count = len(data.get('records', []))
            print(f"[+] SUCCESS! Found {record_count} record(s) in {table_name} table of {base_id} base.")
            
            # Update the .env file with this successful configuration
            update_env_file(base_id, table_name)
            
            return True
        else:
            # Just print a dot to show progress without cluttering the output
            print(".", end="", flush=True)
            return False
    
    except Exception as e:
        print("x", end="", flush=True)
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
    
    # Also update the airtable_sync.py module with the correct configuration
    update_airtable_sync_module(base_id, table_name)

def update_airtable_sync_module(base_id, table_name):
    """Update the airtable_sync.py module with the correct configuration."""
    print("[*] Updating airtable_sync.py module...")
    
    # Path to the airtable_sync.py module
    module_path = "src/modules/airtable_sync.py"
    
    try:
        # Read the current module content
        with open(module_path, "r") as module_file:
            module_content = module_file.read()
        
        # Update the base ID and table name if they are hardcoded
        if "BASE_ID =" in module_content:
            module_content = re.sub(r'BASE_ID = .*', f'BASE_ID = os.getenv("AIRTABLE_BASE_ID", "{base_id}")', module_content)
        
        if "TABLE_NAME =" in module_content:
            module_content = re.sub(r'TABLE_NAME = .*', f'TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME", "{table_name}")', module_content)
        
        # Write the updated content back to the module file
        with open(module_path, "w") as module_file:
            module_file.write(module_content)
        
        print("[+] airtable_sync.py module updated successfully!")
    
    except Exception as e:
        print(f"[-] Error updating airtable_sync.py module: {str(e)}")

def find_airtable_config():
    """Find the correct Airtable configuration by trying different combinations."""
    print("[*] Finding Airtable configuration...")
    print(f"[*] Using API token: {API_TOKEN[:5]}...{API_TOKEN[-5:]}")
    print("[*] Trying different base IDs and table names...")
    
    # Try all combinations of base IDs and table names
    for base_id in BASE_IDS:
        for table_name in TABLE_NAMES:
            if test_base_and_table(base_id, table_name):
                print("\n[+] Found working configuration!")
                return True
    
    print("\n[-] Could not find a working configuration.")
    print("[!] Please check your Airtable workspace and ensure the API token has the correct permissions.")
    return False

if __name__ == "__main__":
    print("[*] Airtable Configuration Finder")
    print("--------------------------------------------------")
    
    # Find the correct Airtable configuration
    find_airtable_config()
