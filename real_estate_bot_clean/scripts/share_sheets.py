"""
Script to share Google Sheets with a specified email address
"""
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json

def share_sheet(drive_service, sheet_id, email):
    """Share a Google Sheet with specified email address."""
    try:
        permission = {
            'type': 'user',
            'role': 'writer',
            'emailAddress': email
        }
        
        drive_service.permissions().create(
            fileId=sheet_id,
            body=permission,
            fields='id'
        ).execute()
        
        print(f"Successfully shared sheet {sheet_id}")
        return True
    except Exception as e:
        print(f"Error sharing sheet {sheet_id}: {str(e)}")
        return False

def main():
    # Initialize Drive API
    SCOPES = ['https://www.googleapis.com/auth/drive.file']
    creds = Credentials.from_service_account_file(
        'credentials/sheets-service-account.json',
        scopes=SCOPES
    )
    drive_service = build('drive', 'v3', credentials=creds)
    
    # Load sheet IDs from file
    with open('sheet_ids.json', 'r') as f:
        sheets = json.load(f)
    
    # Email to share with
    email = 'trippered6778@gmail.com'
    
    # Share each sheet
    for name, sheet_id in sheets.items():
        print(f"\nSharing {name}...")
        if share_sheet(drive_service, sheet_id, email):
            print(f"You can access the sheet at: https://docs.google.com/spreadsheets/d/{sheet_id}")
            print("This sheet contains:")
            if "Property Configuration" in name:
                print("- Property Types (ATTOM/Redfin mappings, min requirements)")
                print("- Property Features (value multipliers for amenities)")
            elif "Market Data" in name:
                print("- Market Types (hot, stable, emerging markets)")
                print("- Location Data (ZIP codes with market classifications)")
            elif "Deal Analysis" in name:
                print("- Analysis Rules (market-specific evaluation criteria)")
                print("- Repair Estimates (standardized cost data)")

if __name__ == '__main__':
    main()
