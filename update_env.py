"""Update .env file with new Airtable token"""

import os
import re
from dotenv import load_dotenv

# Load current environment variables
load_dotenv()

# New token provided by the user
new_token = "pat9OLKV71ObxCkMZ.e314f823e591c8e1648770d26d6e6671da9326f7f6ac17b7b8f21bb06c391385"

# Correct base ID for Real Estate API Tracker
new_base_id = "app0TO0hhThd6Qzym"

# Get current values
current_base_id = os.getenv("AIRTABLE_BASE_ID", "")
current_table_name = os.getenv("AIRTABLE_TABLE_NAME", "")

# Read the current .env file
env_path = ".env"
try:
    with open(env_path, "r") as env_file:
        env_content = env_file.read()
except FileNotFoundError:
    env_content = ""

# Update the Airtable API key
if "AIRTABLE_API_KEY" in env_content:
    env_content = re.sub(r'AIRTABLE_API_KEY=.*', f'AIRTABLE_API_KEY={new_token}', env_content)
else:
    env_content += f"\nAIRTABLE_API_KEY={new_token}"

# Update the Airtable base ID
if "AIRTABLE_BASE_ID" in env_content:
    env_content = re.sub(r'AIRTABLE_BASE_ID=.*', f'AIRTABLE_BASE_ID={new_base_id}', env_content)
else:
    env_content += f"\nAIRTABLE_BASE_ID={new_base_id}"

# Ensure USE_AIRTABLE is set to true
if "USE_AIRTABLE" in env_content:
    env_content = re.sub(r'USE_AIRTABLE=.*', 'USE_AIRTABLE=true', env_content)
else:
    env_content += "\nUSE_AIRTABLE=true"

# Write the updated content back to the .env file
with open(env_path, "w") as env_file:
    env_file.write(env_content)

print("[+] .env file updated successfully!")
print(f"[*] AIRTABLE_API_KEY updated to: {new_token[:5]}...{new_token[-5:]}")
print(f"[*] Current AIRTABLE_BASE_ID: {current_base_id}")
print(f"[*] Current AIRTABLE_TABLE_NAME: {current_table_name}")
print("[*] USE_AIRTABLE: true")
