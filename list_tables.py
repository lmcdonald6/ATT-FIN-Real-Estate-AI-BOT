"""List Tables in Airtable Base

This script lists all tables in the specified Airtable base and creates necessary tables if they don't exist.
"""

import os
import requests
import json
from dotenv import load_dotenv
from urllib.parse import quote

# Load environment variables
load_dotenv()

# Airtable API configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")
BASE_ID = os.getenv("AIRTABLE_BASE_ID")

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def list_tables():
    """List all tables in the specified base."""
    print(f"[*] Using API token: {API_KEY[:5]}...{API_KEY[-5:]}")
    print(f"[*] Base ID: {BASE_ID}")
    
    # Try to list tables using the meta API
    tables_url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    print(f"[*] Trying to access: {tables_url}")
    
    try:
        response = requests.get(tables_url, headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            tables = data.get('tables', [])
            
            print(f"[+] Found {len(tables)} tables in base:")
            for table in tables:
                table_id = table.get('id')
                table_name = table.get('name')
                print(f"    - {table_name} (ID: {table_id})")
                
                # Check if this is the Market Analysis table
                if table_name == "Market Analysis":
                    update_env_file(table_name=table_name)
                    print(f"    [+] Found Market Analysis table! Updated .env file.")
            
            return tables
        else:
            print("[-] Failed to list tables. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
            return []
    except Exception as e:
        print(f"[-] Error: {str(e)}")
        return []

def create_market_analysis_table():
    """Create the Market Analysis table if it doesn't exist."""
    tables = list_tables()
    
    # Check if Market Analysis table already exists
    for table in tables:
        if table.get('name') == "Market Analysis":
            print("[*] Market Analysis table already exists.")
            return True
    
    print("\n[*] Creating Market Analysis table...")
    
    # Define the table structure
    table_data = {
        "name": "Market Analysis",
        "description": "Real estate market analysis data",
        "fields": [
            {"name": "Region", "type": "singleLineText"},
            {"name": "Final Score", "type": "number", "options": {"precision": 1}},
            {"name": "Market Phase", "type": "singleLineText"},
            {"name": "Risk Level", "type": "singleLineText"},
            {"name": "Trend Score", "type": "number", "options": {"precision": 1}},
            {"name": "Economic Score", "type": "number", "options": {"precision": 1}},
            {"name": "PTR Ratio", "type": "number", "options": {"precision": 2}},
            {"name": "Cap Rate", "type": "number", "options": {"precision": 2}},
            {"name": "Monthly Sales", "type": "number"},
            {"name": "Inventory Level", "type": "singleLineText"},
            {"name": "Avg Appreciation", "type": "number", "options": {"precision": 2}},
            {"name": "Property Value", "type": "number"},
            {"name": "Monthly Rent", "type": "number"},
            {"name": "Annual Income", "type": "number"},
            {"name": "Timestamp", "type": "singleLineText"}
        ]
    }
    
    # Create the table
    create_table_url = f"https://api.airtable.com/v0/meta/bases/{BASE_ID}/tables"
    
    try:
        response = requests.post(create_table_url, json=table_data, headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code == 200:
            table_data = response.json()
            table_id = table_data.get('id')
            table_name = table_data.get('name')
            print(f"[+] Table created successfully! Name: {table_name}, ID: {table_id}")
            
            # Update the .env file with the new table name
            update_env_file(table_name=table_name)
            
            return True
        else:
            print("[-] Failed to create table. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
            return False
    
    except Exception as e:
        print(f"[-] Error creating table: {str(e)}")
        return False

def update_env_file(table_name=None):
    """Update the .env file with the table name."""
    if not table_name:
        return
    
    print("[*] Updating .env file...")
    
    # Read the current .env file
    env_path = ".env"
    try:
        with open(env_path, "r") as env_file:
            env_content = env_file.read()
    except FileNotFoundError:
        env_content = ""
    
    # Update the table name
    import re
    
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

def test_table_access():
    """Test access to the Market Analysis table."""
    print("\n[*] Testing access to Market Analysis table...")
    
    # Get the table name from .env
    table_name = os.getenv("AIRTABLE_TABLE_NAME", "Market Analysis")
    
    # URL-encode the table name
    encoded_table_name = quote(table_name)
    
    # Construct the URL
    url = f"https://api.airtable.com/v0/{BASE_ID}/{encoded_table_name}"
    print(f"[*] URL: {url}")
    
    try:
        response = requests.get(f"{url}?maxRecords=1", headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        
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
            except:
                print(response.text)
            return False
    
    except Exception as e:
        print(f"[-] Error accessing table: {str(e)}")
        return False

def create_sample_record():
    """Create a sample record in the Market Analysis table."""
    print("\n[*] Creating sample record in Market Analysis table...")
    
    # Get the table name from .env
    table_name = os.getenv("AIRTABLE_TABLE_NAME", "Market Analysis")
    
    # URL-encode the table name
    encoded_table_name = quote(table_name)
    
    # Construct the URL
    url = f"https://api.airtable.com/v0/{BASE_ID}/{encoded_table_name}"
    
    # Create a sample record
    from datetime import datetime
    
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
        response = requests.post(url, json=record_data, headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            record_id = data.get('id')
            print(f"[+] Sample record created successfully! ID: {record_id}")
            return True
        else:
            print("[-] Failed to create sample record. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except:
                print(response.text)
            return False
    
    except Exception as e:
        print(f"[-] Error creating sample record: {str(e)}")
        return False

def main():
    print("[*] Airtable Table Manager")
    print("--------------------------------------------------")
    
    # List tables in the base
    tables = list_tables()
    
    # Create Market Analysis table if it doesn't exist
    if not any(table.get('name') == "Market Analysis" for table in tables):
        create_market_analysis_table()
    
    # Test access to the Market Analysis table
    if test_table_access():
        # Ask if user wants to create a sample record
        create_record = input("\nDo you want to create a sample record? (y/n): ")
        if create_record.lower() == 'y':
            create_sample_record()
    
    print("\n[*] Airtable setup complete!")
    print("[*] You can now use the Airtable integration in your application.")

if __name__ == "__main__":
    main()
