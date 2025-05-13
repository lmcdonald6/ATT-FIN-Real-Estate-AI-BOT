"""Airtable Sync Test Script

This script tests the Airtable integration by sending a mock market analysis record.
"""

import os
import requests
import json
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Airtable API configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")
TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")

# Fix for already URL-encoded table name in .env
if "%20" in TABLE_NAME:
    TABLE_NAME = TABLE_NAME.replace("%20", " ")

# Airtable API endpoint
import urllib.parse
TABLE_NAME_ENCODED = urllib.parse.quote(TABLE_NAME)
BASE_URL = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME_ENCODED}"

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# Print API key format for debugging (without revealing full key)
print(f"[*] API Key format check: {API_KEY[:10]}...{API_KEY[-5:]}")

# First, let's try to list all workspaces and bases
def list_workspaces_and_bases():
    print("[*] Attempting to list workspaces and bases...")
    
    # Check for workspace named 'Real Estate API Tracker'
    workspace_url = "https://api.airtable.com/v0/meta/workspaces"
    try:
        response = requests.get(workspace_url, headers=HEADERS)
        print(f"[*] Workspace API response status: {response.status_code}")
        
        if response.status_code == 200:
            workspaces = response.json().get('workspaces', [])
            print(f"[+] Found {len(workspaces)} workspaces")
            
            target_workspace = None
            for workspace in workspaces:
                workspace_id = workspace.get('id')
                workspace_name = workspace.get('name')
                print(f"    - {workspace_name} (ID: {workspace_id})")
                
                if workspace_name == "Real Estate API Tracker":
                    target_workspace = workspace_id
                    print(f"    [+] Found target workspace: {workspace_name} (ID: {workspace_id})")
            
            if target_workspace:
                # List bases in the target workspace
                bases_url = f"https://api.airtable.com/v0/meta/workspaces/{target_workspace}/bases"
                bases_response = requests.get(bases_url, headers=HEADERS)
                
                if bases_response.status_code == 200:
                    bases = bases_response.json().get('bases', [])
                    print(f"    [+] Found {len(bases)} bases in workspace")
                    
                    for base in bases:
                        base_id = base.get('id')
                        base_name = base.get('name')
                        print(f"        - {base_name} (ID: {base_id})")
                        
                        # List tables in this base
                        tables_url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
                        tables_response = requests.get(tables_url, headers=HEADERS)
                        
                        if tables_response.status_code == 200:
                            tables = tables_response.json().get('tables', [])
                            print(f"            Found {len(tables)} tables:")
                            
                            for table in tables:
                                table_id = table.get('id')
                                table_name = table.get('name')
                                print(f"                * {table_name} (ID: {table_id})")
                        else:
                            print(f"            [-] Failed to list tables for base {base_id}. Status: {tables_response.status_code}")
                else:
                    print(f"    [-] Failed to list bases in workspace. Status: {bases_response.status_code}")
        else:
            print("[-] Failed to list workspaces. Response:")
            try:
                print(response.json())
            except ValueError:
                print(response.text[:200])
    
    except Exception as e:
        print(f"[-] Error listing workspaces: {str(e)}")

# Create a mock market analysis record
market_record = {
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

# Function to sync record with Airtable
def sync_record(record_data):
    """Sync a record with Airtable."""
    # Prepare data for Airtable API
    payload = {
        "fields": record_data
    }
    
    # Print debugging information
    print("[*] API Request Details:")
    print(f"    URL: {BASE_URL}")
    print(f"    Headers: Authorization: Bearer {API_KEY[:5]}...{API_KEY[-5:]}")
    print(f"    Payload sample: {list(record_data.keys())[:5]}")
    
    try:
        # Create a new record
        print("[*] Sending record to Airtable...")
        response = requests.post(BASE_URL, json=payload, headers=HEADERS)
        
        # Print response status and headers for debugging
        print(f"[*] Response status: {response.status_code}")
        print(f"[*] Response headers: {dict(response.headers)}")
        
        # Check if we got a response body
        try:
            response_json = response.json()
            print(f"[*] Response body: {response_json}")
        except ValueError:
            print(f"[*] Response body (text): {response.text[:100]}")
        
        # Raise exception for HTTP errors
        response.raise_for_status()
        
        print("[+] Record synced successfully!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"[-] Error syncing record to Airtable: {str(e)}")
        if hasattr(e, 'response') and e.response is not None:
            try:
                error_details = e.response.json()
                print(f"[-] Error details: {error_details}")
                return {"status": "error", "message": str(e), "details": error_details}
            except ValueError:
                print(f"[-] Error response text: {e.response.text[:100]}")
        return {"status": "error", "message": str(e)}

# Main execution
if __name__ == "__main__":
    print("[*] Real Estate Market Analysis - Airtable Sync Test")
    print("--------------------------------------------------")
    
    # Step 1: List workspaces and bases to find the correct IDs
    list_workspaces_and_bases()
    
    print("\n--------------------------------------------------")
    print(f"[*] Currently configured Base ID: {BASE_ID}")
    print(f"[*] Currently configured Table: {TABLE_NAME}")
    print("--------------------------------------------------")
    
    # Ask user if they want to proceed with the sync using current settings
    proceed = input("\nDo you want to proceed with the record sync using these settings? (y/n): ")
    
    if proceed.lower() == 'y':
        # Step 2: Sync the record
        print("\n[*] Proceeding with record sync...")
        response = sync_record(market_record)
        
        # Step 3: Print the response
        print("\n[*] Airtable API Response:")
        print(json.dumps(response, indent=2))
    else:
        print("\n[*] Record sync cancelled.")
        print("[*] Please update the .env file with the correct Base ID and Table Name.")
