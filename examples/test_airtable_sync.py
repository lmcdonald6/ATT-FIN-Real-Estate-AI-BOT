import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables from .env file
project_root = Path(__file__).parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

from modules.analyze_market import analyze_market
from modules.market_export_formatter import format_market_export
from modules.airtable_sync import sync_record

# Step 1: Analyze a market
print("🔍 Analyzing Atlanta market...")
result = analyze_market("Atlanta", rent=2400, value=330000, income=85000)

# Step 2: Format the result for Airtable
print("📊 Formatting results for Airtable...")
airtable_row = format_market_export(result.__dict__)

# Step 3: Sync it
print("🔁 Sending record to Airtable...")
response = sync_record(airtable_row)

# Step 4: Confirm success
print("✅ Record synced! Airtable response:")
print(response)
