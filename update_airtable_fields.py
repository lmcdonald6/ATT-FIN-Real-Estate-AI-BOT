"""Update Airtable Fields

This script creates a new record in the Market Analysis table with all the required fields.
Airtable will automatically create these fields if they don't exist.
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

def create_record_with_fields():
    """Create a record with all the required fields."""
    print("[*] Creating record with all required fields...")
    print(f"[*] API Key: {API_KEY[:5]}...{API_KEY[-5:]}")
    print(f"[*] Base ID: {BASE_ID}")
    print(f"[*] Table ID: {TABLE_ID}")
    
    # Construct the URL
    url = f"https://api.airtable.com/v0/{BASE_ID}/{TABLE_ID}"
    print(f"[*] URL: {url}")
    
    # Current timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Create a record with all the required fields
    # Note: Airtable will automatically create these fields if they don't exist
    record_data = {
        "fields": {
            # Skip Record ID and Date since they're computed
            "Region": "Atlanta",
            "Score": 78.5,
            "Phase": "Growth",
            "Risk": "Moderate",
            "TrendScore": 82.3,
            "EconomicScore": 75.6,
            "PTRRatio": 11.45,
            "CapRate": 6.8,
            "MonthlySales": 1250,
            "Inventory": "Medium",
            "AvgAppreciation": 4.2,
            "PropertyValue": 330000,
            "MonthlyRent": 2400,
            "AnnualIncome": 85000,
            "Notes": "This record was created to add all the required fields for the market analysis tool."
        }
    }
    
    try:
        # Create the record
        response = requests.post(url, json=record_data, headers=HEADERS)
        print(f"[*] Response status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            data = response.json()
            record_id = data.get('id')
            print(f"[+] Record created successfully! ID: {record_id}")
            print("[*] Created record:")
            print(json.dumps(data, indent=2))
            
            # Update the airtable_sync.py module with the correct field names
            update_airtable_sync_module()
            
            return True
        else:
            print("[-] Failed to create record. Response:")
            try:
                print(json.dumps(response.json(), indent=2))
            except ValueError:
                print(response.text)
            return False
    
    except Exception as e:
        print(f"[-] Error creating record: {str(e)}")
        return False

def update_airtable_sync_module():
    """Update the airtable_sync.py module with the correct field names."""
    print("\n[*] Updating airtable_sync.py module with correct field names...")
    
    # Path to the airtable_sync.py module
    module_path = "src/modules/airtable_sync.py"
    
    try:
        # Read the current module content
        with open(module_path, "r") as module_file:
            module_content = module_file.read()
        
        # Define field mappings (original field name -> Airtable field name)
        field_mappings = {
            "Region": "Region",
            "Final Score": "Final_Score",
            "Market Phase": "Market_Phase",
            "Risk Level": "Risk_Level",
            "Trend Score": "Trend_Score",
            "Economic Score": "Economic_Score",
            "PTR Ratio": "PTR_Ratio",
            "Cap Rate": "Cap_Rate",
            "Monthly Sales": "Monthly_Sales",
            "Inventory Level": "Inventory_Level",
            "Avg Appreciation": "Avg_Appreciation",
            "Property Value": "Property_Value",
            "Monthly Rent": "Monthly_Rent",
            "Annual Income": "Annual_Income",
            "Timestamp": "Timestamp"
        }
        
        # Add a field mapping dictionary to the module
        field_mapping_code = "\n# Field mappings for Airtable\nFIELD_MAPPINGS = {\n"
        for original, airtable in field_mappings.items():
            field_mapping_code += f"    \"{original}\": \"{airtable}\",\n"
        field_mapping_code += "}\n"
        
        # Check if the field mappings already exist
        if "FIELD_MAPPINGS = {" not in module_content:
            # Find a good place to insert the field mappings (after the imports)
            import_section_end = module_content.find("# Airtable API configuration")
            if import_section_end > 0:
                module_content = module_content[:import_section_end] + field_mapping_code + "\n" + module_content[import_section_end:]
            else:
                # If we can't find a good place, just append it to the end
                module_content += "\n" + field_mapping_code
        
        # Update the sync_record function to use the field mappings
        sync_record_start = module_content.find("def sync_record")
        sync_record_end = module_content.find("def get_records")
        
        if sync_record_start > 0 and sync_record_end > sync_record_start:
            sync_record_code = module_content[sync_record_start:sync_record_end]
            
            # Check if we need to add the field mapping logic
            if "FIELD_MAPPINGS.get" not in sync_record_code:
                # Find the place where we prepare the payload
                payload_section = sync_record_code.find("# Prepare data for Airtable API")
                if payload_section > 0:
                    # Find the end of the payload section
                    payload_end = sync_record_code.find("try:", payload_section)
                    if payload_end > payload_section:
                        # Insert the field mapping logic before the try block
                        field_mapping_logic = """    # Map field names to Airtable field names
    mapped_record_data = {}
    for key, value in record_data.items():
        mapped_key = FIELD_MAPPINGS.get(key, key)  # Use original key if no mapping exists
        mapped_record_data[mapped_key] = value
    
    # Prepare data for Airtable API
    payload = {
        "fields": mapped_record_data
    }
    
"""
                        
                        # Replace the original payload section
                        original_payload_section = sync_record_code[payload_section:payload_end]
                        sync_record_code = sync_record_code.replace(original_payload_section, field_mapping_logic)
                        
                        # Update the module content
                        module_content = module_content[:sync_record_start] + sync_record_code + module_content[sync_record_end:]
        
        # Write the updated content back to the module file
        with open(module_path, "w") as module_file:
            module_file.write(module_content)
        
        print("[+] airtable_sync.py module updated successfully!")
        return True
    
    except Exception as e:
        print(f"[-] Error updating airtable_sync.py module: {str(e)}")
        return False

if __name__ == "__main__":
    print("[*] Airtable Fields Update")
    print("--------------------------------------------------")
    
    # Create a record with all the required fields
    create_record_with_fields()
