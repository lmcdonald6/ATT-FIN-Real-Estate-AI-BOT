"""Update Airtable Configuration

This script helps update the Airtable configuration in the .env file.
"""

import os
import re
from dotenv import load_dotenv

# Load current environment variables
load_dotenv()

def update_env_file(api_key=None, base_id=None, table_name=None):
    """Update the .env file with new Airtable configuration."""
    # Get current values
    current_api_key = os.getenv("AIRTABLE_API_KEY", "")
    current_base_id = os.getenv("AIRTABLE_BASE_ID", "")
    current_table_name = os.getenv("AIRTABLE_TABLE_NAME", "")
    
    # Use provided values or keep current ones
    new_api_key = api_key if api_key else current_api_key
    new_base_id = base_id if base_id else current_base_id
    new_table_name = table_name if table_name else current_table_name
    
    # Read the current .env file
    env_path = ".env"
    try:
        with open(env_path, "r") as env_file:
            env_content = env_file.read()
    except FileNotFoundError:
        env_content = ""
    
    # Update or add the Airtable configuration
    if "AIRTABLE_API_KEY" in env_content:
        env_content = re.sub(r'AIRTABLE_API_KEY=.*', f'AIRTABLE_API_KEY={new_api_key}', env_content)
    else:
        env_content += f"\nAIRTABLE_API_KEY={new_api_key}"
    
    if "AIRTABLE_BASE_ID" in env_content:
        env_content = re.sub(r'AIRTABLE_BASE_ID=.*', f'AIRTABLE_BASE_ID={new_base_id}', env_content)
    else:
        env_content += f"\nAIRTABLE_BASE_ID={new_base_id}"
    
    if "AIRTABLE_TABLE_NAME" in env_content:
        env_content = re.sub(r'AIRTABLE_TABLE_NAME=.*', f'AIRTABLE_TABLE_NAME={new_table_name}', env_content)
    else:
        env_content += f"\nAIRTABLE_TABLE_NAME={new_table_name}"
    
    # Ensure USE_AIRTABLE is set to true
    if "USE_AIRTABLE" in env_content:
        env_content = re.sub(r'USE_AIRTABLE=.*', 'USE_AIRTABLE=true', env_content)
    else:
        env_content += "\nUSE_AIRTABLE=true"
    
    # Write the updated content back to the .env file
    with open(env_path, "w") as env_file:
        env_file.write(env_content)
    
    print("[+] .env file updated successfully!")
    print(f"[*] AIRTABLE_API_KEY: {new_api_key[:5]}...{new_api_key[-5:] if new_api_key else ''}")
    print(f"[*] AIRTABLE_BASE_ID: {new_base_id}")
    print(f"[*] AIRTABLE_TABLE_NAME: {new_table_name}")
    print("[*] USE_AIRTABLE: true")

def main():
    print("[*] Airtable Configuration Update Tool")
    print("--------------------------------------------------")
    
    # Get current values
    current_api_key = os.getenv("AIRTABLE_API_KEY", "")
    current_base_id = os.getenv("AIRTABLE_BASE_ID", "")
    current_table_name = os.getenv("AIRTABLE_TABLE_NAME", "")
    
    print("Current Airtable Configuration:")
    print(f"API Key: {current_api_key[:5]}...{current_api_key[-5:] if current_api_key else ''}")
    print(f"Base ID: {current_base_id}")
    print(f"Table Name: {current_table_name}")
    print("--------------------------------------------------")
    
    # Get new values from user input
    print("Enter new values (or press Enter to keep current values):")
    new_api_key = input("New Personal Access Token: ").strip()
    new_base_id = input("New Base ID: ").strip()
    new_table_name = input("New Table Name: ").strip()
    
    # Update the .env file
    update_env_file(
        api_key=new_api_key if new_api_key else None,
        base_id=new_base_id if new_base_id else None,
        table_name=new_table_name if new_table_name else None
    )

if __name__ == "__main__":
    main()
