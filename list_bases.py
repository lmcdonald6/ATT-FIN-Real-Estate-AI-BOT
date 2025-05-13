"""List all Airtable bases accessible with the current token"""

import os
import json
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Airtable API configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")

# Headers for API requests with Personal Access Token
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def list_bases():
    """List all bases accessible with the current token."""
    print("[*] Listing all accessible Airtable bases...")
    print(f"[*] Using API key: {API_KEY[:5]}...{API_KEY[-5:]}")
    
    # Try the new Airtable API endpoint for listing bases
    url = "https://api.airtable.com/v0/meta/bases"
    
    try:
        response = requests.get(url, headers=HEADERS)
        
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            bases = data.get('bases', [])
            
            print(f"[+] Found {len(bases)} accessible bases:")
            for base in bases:
                base_id = base.get('id')
                base_name = base.get('name')
                print(f"    - {base_name} (ID: {base_id})")
                
                # Try to list tables in this base
                list_tables(base_id)
            
            return True
        else:
            print("[-] Failed to list bases. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text[:200])
            
            # Try alternative approach - list bases by workspace
            print("\n[*] Trying alternative approach - listing workspaces...")
            list_workspaces()
            
            return False
    
    except Exception as e:
        print(f"[-] Error listing bases: {str(e)}")
        return False

def list_workspaces():
    """List all workspaces accessible with the current token."""
    url = "https://api.airtable.com/v0/meta/workspaces"
    
    try:
        response = requests.get(url, headers=HEADERS)
        
        print(f"[*] Workspace response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            workspaces = data.get('workspaces', [])
            
            print(f"[+] Found {len(workspaces)} accessible workspaces:")
            for workspace in workspaces:
                workspace_id = workspace.get('id')
                workspace_name = workspace.get('name')
                print(f"    - {workspace_name} (ID: {workspace_id})")
                
                # List bases in this workspace
                list_bases_in_workspace(workspace_id)
        else:
            print("[-] Failed to list workspaces. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text[:200])
    
    except Exception as e:
        print(f"[-] Error listing workspaces: {str(e)}")

def list_bases_in_workspace(workspace_id):
    """List all bases in a specific workspace."""
    url = f"https://api.airtable.com/v0/meta/workspaces/{workspace_id}/bases"
    
    try:
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            bases = data.get('bases', [])
            
            print(f"      Found {len(bases)} bases in workspace:")
            for base in bases:
                base_id = base.get('id')
                base_name = base.get('name')
                print(f"        - {base_name} (ID: {base_id})")
                
                # List tables in this base
                list_tables(base_id)
        else:
            print(f"      [-] Failed to list bases in workspace. Status: {response.status_code}")
    
    except Exception as e:
        print(f"      [-] Error listing bases in workspace: {str(e)}")

def list_tables(base_id):
    """List all tables in a specific base."""
    url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    
    try:
        response = requests.get(url, headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            tables = data.get('tables', [])
            
            print(f"          Found {len(tables)} tables in base:")
            for table in tables:
                table_id = table.get('id')
                table_name = table.get('name')
                print(f"              * {table_name} (ID: {table_id})")
        else:
            print(f"          [-] Failed to list tables in base. Status: {response.status_code}")
    
    except Exception as e:
        print(f"          [-] Error listing tables in base: {str(e)}")

# Try direct access to the configured base
def try_direct_access():
    """Try direct access to the configured base and table."""
    BASE_ID = os.getenv("AIRTABLE_BASE_ID")
    TABLE_NAME = os.getenv("AIRTABLE_TABLE_NAME")
    
    if "%20" in TABLE_NAME:
        TABLE_NAME = TABLE_NAME.replace("%20", " ")
    
    print(f"\n[*] Trying direct access to configured base and table...")
    print(f"[*] Base ID: {BASE_ID}")
    print(f"[*] Table Name: {TABLE_NAME}")
    
    # Try to access the base directly
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_NAME}"
    
    try:
        response = requests.get(f"{url}?maxRecords=1", headers=HEADERS)
        
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code == 200:
            print("[+] Successfully accessed the configured base and table!")
            return True
        else:
            print("[-] Failed to access the configured base and table. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text[:200])
            return False
    
    except Exception as e:
        print(f"[-] Error accessing base: {str(e)}")
        return False

if __name__ == "__main__":
    print("[*] Airtable Base and Table Listing Tool")
    print("--------------------------------------------------")
    
    # List all accessible bases
    list_bases()
    
    # Try direct access to the configured base and table
    try_direct_access()
