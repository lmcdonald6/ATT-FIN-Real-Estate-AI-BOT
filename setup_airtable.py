"""Setup Airtable Structure

This script helps set up the correct Airtable structure for the Real Estate API Tracker.
It will create the necessary tables and fields if they don't exist.
"""

import os
import json
import requests
import time
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()

# Airtable API configuration
API_KEY = os.getenv("AIRTABLE_API_KEY")

# Headers for API requests
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def create_base(name="Real Estate API Tracker"):
    """Create a new Airtable base."""
    print(f"[*] Creating new base: {name}")
    
    # First, we need to get the workspace ID
    workspaces_url = "https://api.airtable.com/v0/meta/workspaces"
    
    try:
        response = requests.get(workspaces_url, headers=HEADERS)
        
        if response.status_code == 200:
            workspaces = response.json().get('workspaces', [])
            
            if not workspaces:
                print("[-] No workspaces found. Please create a workspace in Airtable first.")
                return None
            
            # Use the first workspace
            workspace_id = workspaces[0]['id']
            workspace_name = workspaces[0]['name']
            print(f"[+] Using workspace: {workspace_name} (ID: {workspace_id})")
            
            # Create the base
            create_base_url = f"https://api.airtable.com/v0/meta/workspaces/{workspace_id}/bases"
            payload = {
                "name": name
            }
            
            create_response = requests.post(create_base_url, json=payload, headers=HEADERS)
            
            if create_response.status_code == 200:
                base_data = create_response.json()
                base_id = base_data.get('id')
                print(f"[+] Base created successfully! ID: {base_id}")
                
                # Update the .env file with the new base ID
                update_env_file(base_id=base_id)
                
                return base_id
            else:
                print(f"[-] Failed to create base. Status: {create_response.status_code}")
                try:
                    print(create_response.json())
                except:
                    print(create_response.text)
                return None
        else:
            print(f"[-] Failed to list workspaces. Status: {response.status_code}")
            return None
    
    except Exception as e:
        print(f"[-] Error creating base: {str(e)}")
        return None

def create_market_analysis_table(base_id):
    """Create the Market Analysis table in the specified base."""
    print(f"[*] Creating Market Analysis table in base: {base_id}")
    
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
    create_table_url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    
    try:
        response = requests.post(create_table_url, json=table_data, headers=HEADERS)
        
        if response.status_code == 200:
            table_data = response.json()
            table_id = table_data.get('id')
            table_name = table_data.get('name')
            print(f"[+] Table created successfully! Name: {table_name}, ID: {table_id}")
            
            # Update the .env file with the new table name
            update_env_file(table_name=table_name)
            
            return table_name
        else:
            print(f"[-] Failed to create table. Status: {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)
            return None
    
    except Exception as e:
        print(f"[-] Error creating table: {str(e)}")
        return None

def create_properties_table(base_id):
    """Create the Properties table in the specified base."""
    print(f"[*] Creating Properties table in base: {base_id}")
    
    # Define the table structure
    table_data = {
        "name": "Properties",
        "description": "Real estate property data",
        "fields": [
            {"name": "Property Name", "type": "singleLineText"},
            {"name": "Address", "type": "singleLineText"},
            {"name": "City", "type": "singleLineText"},
            {"name": "State", "type": "singleLineText"},
            {"name": "Zip Code", "type": "singleLineText"},
            {"name": "Property Type", "type": "singleLineText"},
            {"name": "Bedrooms", "type": "number"},
            {"name": "Bathrooms", "type": "number", "options": {"precision": 1}},
            {"name": "Square Feet", "type": "number"},
            {"name": "Lot Size", "type": "number", "options": {"precision": 2}},
            {"name": "Year Built", "type": "number"},
            {"name": "Purchase Price", "type": "number"},
            {"name": "Current Value", "type": "number"},
            {"name": "Monthly Rent", "type": "number"},
            {"name": "Cap Rate", "type": "number", "options": {"precision": 2}},
            {"name": "Cash Flow", "type": "number"},
            {"name": "ROI", "type": "number", "options": {"precision": 2}},
            {"name": "Notes", "type": "multilineText"}
        ]
    }
    
    # Create the table
    create_table_url = f"https://api.airtable.com/v0/meta/bases/{base_id}/tables"
    
    try:
        response = requests.post(create_table_url, json=table_data, headers=HEADERS)
        
        if response.status_code == 200:
            table_data = response.json()
            table_id = table_data.get('id')
            table_name = table_data.get('name')
            print(f"[+] Table created successfully! Name: {table_name}, ID: {table_id}")
            return table_name
        else:
            print(f"[-] Failed to create table. Status: {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)
            return None
    
    except Exception as e:
        print(f"[-] Error creating table: {str(e)}")
        return None

def update_env_file(base_id=None, table_name=None):
    """Update the .env file with the new base ID and table name."""
    if not base_id and not table_name:
        return
    
    print("[*] Updating .env file...")
    
    # Read the current .env file
    env_path = ".env"
    try:
        with open(env_path, "r") as env_file:
            env_content = env_file.read()
    except FileNotFoundError:
        env_content = ""
    
    # Update the base ID and table name
    import re
    
    if base_id:
        if "AIRTABLE_BASE_ID" in env_content:
            env_content = re.sub(r'AIRTABLE_BASE_ID=.*', f'AIRTABLE_BASE_ID={base_id}', env_content)
        else:
            env_content += f"\nAIRTABLE_BASE_ID={base_id}"
    
    if table_name:
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

def create_sample_record(base_id, table_name):
    """Create a sample record in the specified table."""
    print(f"[*] Creating sample record in {table_name}...")
    
    # URL-encode the table name
    import urllib.parse
    encoded_table_name = urllib.parse.quote(table_name)
    
    # Construct the URL
    url = f"https://api.airtable.com/v0/{base_id}/{encoded_table_name}"
    
    # Create a sample record based on the table name
    if table_name == "Market Analysis":
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
    elif table_name == "Properties":
        record_data = {
            "fields": {
                "Property Name": "Sample Property",
                "Address": "123 Main St",
                "City": "Sample City",
                "State": "CA",
                "Zip Code": "90210",
                "Property Type": "Single Family",
                "Bedrooms": 3,
                "Bathrooms": 2.5,
                "Square Feet": 2000,
                "Lot Size": 0.25,
                "Year Built": 2010,
                "Purchase Price": 350000,
                "Current Value": 450000,
                "Monthly Rent": 2800,
                "Cap Rate": 7.5,
                "Cash Flow": 850,
                "ROI": 12.5,
                "Notes": "This is a sample property record."
            }
        }
    else:
        print(f"[-] Unknown table name: {table_name}")
        return False
    
    try:
        # Create the record
        response = requests.post(url, json=record_data, headers=HEADERS)
        
        if response.status_code in [200, 201]:
            record_data = response.json()
            record_id = record_data.get('id')
            print(f"[+] Sample record created successfully! ID: {record_id}")
            return True
        else:
            print(f"[-] Failed to create sample record. Status: {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)
            return False
    
    except Exception as e:
        print(f"[-] Error creating sample record: {str(e)}")
        return False

def test_airtable_connection():
    """Test the Airtable connection with the current configuration."""
    print("[*] Testing Airtable connection...")
    
    # Get the current configuration
    base_id = os.getenv("AIRTABLE_BASE_ID")
    table_name = os.getenv("AIRTABLE_TABLE_NAME")
    
    if not base_id or not table_name:
        print("[-] Missing Airtable configuration. Please set AIRTABLE_BASE_ID and AIRTABLE_TABLE_NAME in .env file.")
        return False
    
    # Fix for URL-encoded table name
    if "%20" in table_name:
        table_name = table_name.replace("%20", " ")
    
    # URL-encode the table name
    import urllib.parse
    encoded_table_name = urllib.parse.quote(table_name)
    
    # Construct the URL
    url = f"https://api.airtable.com/v0/{base_id}/{encoded_table_name}"
    
    try:
        # Try to list records (limit to 1 to minimize data transfer)
        response = requests.get(f"{url}?maxRecords=1", headers=HEADERS)
        
        if response.status_code == 200:
            data = response.json()
            record_count = len(data.get('records', []))
            print(f"[+] Connection successful! Found {record_count} record(s) in {table_name} table.")
            return True
        else:
            print(f"[-] Connection failed. Status: {response.status_code}")
            try:
                print(response.json())
            except:
                print(response.text)
            return False
    
    except Exception as e:
        print(f"[-] Error testing connection: {str(e)}")
        return False

def main():
    print("[*] Airtable Setup Tool")
    print("--------------------------------------------------")
    print(f"[*] Using API token: {API_KEY[:5]}...{API_KEY[-5:] if API_KEY else 'Not set'}")
    
    # First, test the current configuration
    if test_airtable_connection():
        print("[+] Existing Airtable configuration is working!")
        print("[*] You can now use the Airtable integration in your application.")
        return
    
    print("\n[*] Creating new Airtable structure...")
    
    # Create a new base
    base_id = create_base()
    
    if not base_id:
        print("[-] Failed to create base. Please check your API token and try again.")
        return
    
    # Wait a bit for the base to be created
    print("[*] Waiting for base to be ready...")
    time.sleep(5)
    
    # Create the Market Analysis table
    market_table = create_market_analysis_table(base_id)
    
    if not market_table:
        print("[-] Failed to create Market Analysis table.")
        return
    
    # Create the Properties table
    properties_table = create_properties_table(base_id)
    
    # Create sample records
    if market_table:
        create_sample_record(base_id, market_table)
    
    if properties_table:
        create_sample_record(base_id, properties_table)
    
    print("\n[*] Airtable setup complete!")
    print(f"[*] Base ID: {base_id}")
    print(f"[*] Market Analysis Table: {market_table}")
    print(f"[*] Properties Table: {properties_table if properties_table else 'Not created'}")
    print("[*] You can now use the Airtable integration in your application.")

if __name__ == "__main__":
    main()
