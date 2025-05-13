"""Airtable Base Listing Script

This script attempts to list all available bases and tables that the API key has access to.
"""

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Airtable API configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Metadata API endpoint (for listing bases)
META_API_URL = "https://api.airtable.com/v0/meta/bases"

def list_bases():
    """List all bases accessible to the API key."""
    print("[*] Attempting to list all accessible Airtable bases...")
    print(f"[*] Using API key: {API_KEY[:5]}...{API_KEY[-5:]}")
    
    try:
        response = requests.get(META_API_URL, headers=HEADERS)
        
        # Print response status and headers for debugging
        print(f"[*] Response status: {response.status_code}")
        
        # Check if we got a valid response
        if response.status_code == 200:
            bases = response.json().get('bases', [])
            print(f"[+] Found {len(bases)} accessible bases:")
            
            for base in bases:
                base_id = base.get('id')
                base_name = base.get('name')
                print(f"    - {base_name} (ID: {base_id})")
                
                # Try to list tables in this base
                list_tables(base_id)
        else:
            print("[-] Failed to list bases. Response:")
            try:
                print(response.json())
            except ValueError:
                print(response.text[:200])
    
    except Exception as e:
        print(f"[-] Error listing bases: {str(e)}")

def list_tables(base_id):
    """List all tables in a specific base."""
    tables_url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    
    try:
        response = requests.get(tables_url, headers=HEADERS)
        
        if response.status_code == 200:
            tables = response.json().get('tables', [])
            print(f"      Found {len(tables)} tables:")
            
            for table in tables:
                table_id = table.get('id')
                table_name = table.get('name')
                print(f"        * {table_name} (ID: {table_id})")
        else:
            print(f"      [-] Failed to list tables for base {base_id}. Status: {response.status_code}")
    
    except Exception as e:
        print(f"      [-] Error listing tables for base {base_id}: {str(e)}")

if __name__ == "__main__":
    print("[*] Airtable Base and Table Listing Tool")
    print("--------------------------------------------------")
    
    list_bases()
    
    print("\n[*] Checking specific base and table from .env")
    print("--------------------------------------------------")
    BASE_ID = os.getenv("AIRTABLE_BASE_ID")
    TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
    
    print(f"[*] Configured Base ID: {BASE_ID}")
    print(f"[*] Configured Table Name: {TABLE_NAME}")
    
    # Try to access the specific table
    table_url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    try:
        response = requests.get(table_url, headers=HEADERS)
        print(f"[*] Response status for specific base check: {response.status_code}")
        
        if response.status_code == 200:
            tables = response.json().get('tables', [])
            table_names = [table.get('name') for table in tables]
            
            if TABLE_NAME in table_names:
                print(f"[+] Table '{TABLE_NAME}' found in base {BASE_ID}")
            else:
                print(f"[-] Table '{TABLE_NAME}' NOT found in base {BASE_ID}")
                print(f"[*] Available tables: {table_names}")
        else:
            print("[-] Failed to check specific base. Response:")
            try:
                print(response.json())
            except ValueError:
                print(response.text[:200])
    
    except Exception as e:
        print(f"[-] Error checking specific base: {str(e)}")
