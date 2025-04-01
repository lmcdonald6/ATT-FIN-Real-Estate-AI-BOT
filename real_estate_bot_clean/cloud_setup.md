# Google Cloud Project Setup Guide

## 1. Create Google Cloud Project

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Click "Create Project" or select an existing project
3. Name: "Real Estate AI Bot"
4. Click "Create"

## 2. Enable Google Sheets API

1. Go to [Google Cloud Console APIs](https://console.cloud.google.com/apis/library)
2. Search for "Google Sheets API"
3. Click "Enable"

## 3. Create Service Account

1. Go to [IAM & Admin > Service Accounts](https://console.cloud.google.com/iam-admin/serviceaccounts)
2. Click "Create Service Account"
3. Service Account Details:
   - Name: "real-estate-bot"
   - Description: "Service account for Real Estate AI Bot"
4. Click "Create and Continue"
5. Grant Access:
   - Role: "Editor" (for Google Sheets access)
6. Click "Done"

## 4. Create and Download Credentials

1. Find your service account in the list
2. Click the three dots (⋮) > "Manage Keys"
3. Click "Add Key" > "Create New Key"
4. Choose "JSON" format
5. Click "Create"
6. Save the downloaded file as `sheets_cred.json` in the `credentials` folder

## 5. Create Google Sheets

1. Go to [Google Drive](https://drive.google.com)
2. Create 5 new Google Sheets:
   - Market Data
   - Property Data
   - Config
   - Usage Log
   - Alerts

3. Share each sheet:
   - Click "Share"
   - Add service account email (ends with @...iam.gserviceaccount.com)
   - Set role to "Editor"

4. Get Sheet IDs:
   - Open each sheet
   - Copy ID from URL: `https://docs.google.com/spreadsheets/d/[SHEET_ID]/edit`
   - Update `sheet_ids.json` with IDs

## 6. Test Setup

1. Verify credentials:
```python
from src.data.sheets import SheetsManager
sheets = SheetsManager()
# Should initialize without errors
```

2. Test write access:
```python
# Update market data
await sheets.update_market_data('37201', {
    'median_price': 300000,
    'last_updated': '2025-03-15T17:10:20'
})
```

## Security Notes

For MVP:
- Credentials stored locally in `credentials/`
- Basic access controls through service account
- Sheet IDs in version control (for development)

Post-MVP TODOs:
- Move credentials to secure environment variables
- Implement more granular access controls
- Add API key rotation
- Set up audit logging
