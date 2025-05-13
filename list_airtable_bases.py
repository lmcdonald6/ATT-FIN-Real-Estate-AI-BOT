"""List Airtable Bases

This script attempts to list all Airtable bases that the API token has access to.
"""

import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Airtable API configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def list_bases():
    """List all bases accessible with the current token."""
    print(f"[*] Using API token: {API_KEY[:5]}...{API_KEY[-5:]}")
    
    # Try the bases endpoint
    bases_url = "https://api.airtable.com/v0/bases"
    print(f"[*] Trying to access: {bases_url}")
    
    try:
        response = requests.get(bases_url, headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            return True
        else:
            print("[-] Failed to list bases. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
    except Exception as e:
        print(f"[-] Error: {str(e)}")
    
    # Try the meta/bases endpoint
    meta_bases_url = "https://api.airtable.com/v0/meta/bases"
    print(f"\n[*] Trying to access: {meta_bases_url}")
    
    try:
        response = requests.get(meta_bases_url, headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            return True
        else:
            print("[-] Failed to list bases. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
    except Exception as e:
        print(f"[-] Error: {str(e)}")
    
    # Try the meta/workspaces endpoint
    workspaces_url = "https://api.airtable.com/v0/meta/workspaces"
    print(f"\n[*] Trying to access: {workspaces_url}")
    
    try:
        response = requests.get(workspaces_url, headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2))
            return True
        else:
            print("[-] Failed to list workspaces. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
    except Exception as e:
        print(f"[-] Error: {str(e)}")
    
    # Try direct access to specific base IDs
    print("\n[*] Trying direct access to common base IDs...")
    
    # List of possible base IDs to try
    base_ids = [
        "appRealEstateTracker",
        "appRealEstate",
        "app0T00hhThd6Qzym",  # Current configured base ID
        "appRealEstateAPITracker",
        "appRealEstateAPI",
        "appRETracker",
        "appREAPI"
    ]
    
    for base_id in base_ids:
        base_url = f"https://api.airtable.com/v0/{base_id}"
        print(f"[*] Trying base ID: {base_id}")
        
        try:
            response = requests.get(base_url, headers=HEADERS)
            print(f"  - Response status: {response.status_code}")
            
            if response.status_code == 200:
                print(f"[+] Successfully accessed base: {base_id}")
                print("[*] Response:")
                try:
                    print(json.dumps(response.json(), indent=2))
                except:
                    print(response.text)
                return True
        except Exception as e:
            print(f"  - Error: {str(e)}")
    
    return False

def try_common_base_table_combinations():
    """Try common combinations of base IDs and table names."""
    print("\n[*] Trying common base ID and table name combinations...")
    
    # List of possible base IDs to try
    base_ids = [
        "appRealEstateTracker",
        "appRealEstate",
        "app0T00hhThd6Qzym",  # Current configured base ID
        "appRealEstateAPITracker",
        "appRealEstateAPI",
        "appRETracker",
        "appREAPI"
    ]
    
    # List of possible table names to try
    table_names = [
        "Market Analysis",
        "Properties",
        "Investments",
        "Markets",
        "Analysis",
        "Real Estate",
        "Property Analysis"
    ]
    
    for base_id in base_ids:
        for table_name in table_names:
            # URL-encode the table name
            import urllib.parse
            encoded_table_name = urllib.parse.quote(table_name)
            
            # Construct the URL
            url = f"https://api.airtable.com/v0/{base_id}/{encoded_table_name}"
            print(f"[*] Trying: {base_id} / {table_name}")
            
            try:
                response = requests.get(f"{url}?maxRecords=1", headers=HEADERS)
                
                if response.status_code == 200:
                    print(f"[+] SUCCESS! Found table {table_name} in base {base_id}")
                    print("[*] Response:")
                    try:
                        data = response.json()
                        record_count = len(data.get('records', []))
                        print(f"[*] Found {record_count} record(s)")
                        if record_count > 0:
                            print(json.dumps(data['records'][0], indent=2))
                    except:
                        print(response.text)
                    
                    # Update the .env file with this successful configuration
                    update_env_file(base_id, table_name)
                    return True
                else:
                    print(f"  - Failed: {response.status_code}")
            except Exception as e:
                print(f"  - Error: {str(e)}")
    
    return False

def update_env_file(base_id, table_name):
    """Update the .env file with the successful configuration."""
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

def main():
    print("[*] Airtable Base Finder")
    print("--------------------------------------------------")
    
    # Try to list all bases
    if not list_bases():
        print("\n[-] Could not list bases. Trying direct access to common combinations...")
    
    # Try common base ID and table name combinations
    if not try_common_base_table_combinations():
        print("\n[-] Could not find a working combination of base ID and table name.")
        print("[!] Please follow the manual setup guide in airtable_manual_setup.md")

if __name__ == "__main__":
    main()
