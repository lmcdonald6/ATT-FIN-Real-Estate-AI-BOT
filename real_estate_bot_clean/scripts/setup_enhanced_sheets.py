"""
Script to set up enhanced Google Sheets structure for the real estate bot
"""
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json

def create_sheet(service, title, sheets):
    """Create a new Google Sheet with specified worksheets."""
    spreadsheet = {
        'properties': {'title': title},
        'sheets': [{'properties': {'title': name}} for name in sheets]
    }
    
    spreadsheet = service.spreadsheets().create(body=spreadsheet).execute()
    print(f"Created sheet: {title} with ID: {spreadsheet['spreadsheetId']}")
    return spreadsheet['spreadsheetId']

def setup_property_config(service, sheet_id):
    """Set up property configuration sheets."""
    # Property Type Mappings
    values = [
        ['ATTOM Type', 'Redfin Type', 'Display Name', 'Min Beds', 'Min Baths', 'Min SqFt'],
        ['SFR', 'Single Family Residential', 'Single Family Home', '2', '1', '800'],
        ['APT', 'Multi-Family', 'Multi-Family', '2', '1', '600'],
        ['DUPLEX', 'Multi-Family (2-4 units)', 'Duplex', '2', '1', '1000'],
        ['CONDO', 'Condo/Co-op', 'Condo', '1', '1', '500']
    ]
    range_name = 'Property Types!A1:F5'
    body = {'values': values}
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()
    
    # Property Features
    values = [
        ['Feature', 'Value Multiplier', 'Description'],
        ['Pool', '1.15', 'Property has a pool'],
        ['Garage', '1.1', 'Property has a garage'],
        ['Waterfront', '1.25', 'Waterfront property'],
        ['New Construction', '1.2', 'Built within last 2 years']
    ]
    range_name = 'Property Features!A1:C5'
    body = {'values': values}
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()

def setup_market_data(service, sheet_id):
    """Set up market data sheets."""
    # Market Types
    values = [
        ['Market Type', 'Description', 'Base Multiplier'],
        ['Hot', 'High demand, fast appreciation', '1.2'],
        ['Stable', 'Consistent market, steady growth', '1.0'],
        ['Emerging', 'Up-and-coming area', '0.9'],
        ['Cooling', 'Slowing market conditions', '0.85']
    ]
    range_name = 'Market Types!A1:C5'
    body = {'values': values}
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()
    
    # Sample ZIP Codes
    values = [
        ['ZIP Code', 'City', 'State', 'Market Type', 'Price Range Min', 'Price Range Max'],
        ['37201', 'Nashville', 'TN', 'Hot', '300000', '800000'],
        ['37203', 'Nashville', 'TN', 'Hot', '400000', '1000000'],
        ['37206', 'Nashville', 'TN', 'Emerging', '250000', '600000']
    ]
    range_name = 'Location Data!A1:F4'
    body = {'values': values}
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()

def setup_deal_analysis(service, sheet_id):
    """Set up deal analysis configuration."""
    # Analysis Rules
    values = [
        ['Rule Type', 'Condition', 'Action', 'Priority'],
        ['ARV Calculation', 'Hot Market', 'Use 6-month comps only', '1'],
        ['Repair Estimate', 'Age > 30 years', 'Add 15% to base estimate', '2'],
        ['Deal Score', 'Profit Margin > 25%', 'Mark as "Strong Deal"', '1']
    ]
    range_name = 'Analysis Rules!A1:D4'
    body = {'values': values}
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()
    
    # Repair Estimates
    values = [
        ['Category', 'Base Cost', 'Unit', 'Notes'],
        ['Roof', '8000', 'per job', 'Basic replacement'],
        ['HVAC', '6000', 'per unit', 'Full system'],
        ['Kitchen', '15000', 'per room', 'Mid-grade remodel'],
        ['Bathroom', '8000', 'per room', 'Full remodel']
    ]
    range_name = 'Repair Estimates!A1:D5'
    body = {'values': values}
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id, range=range_name,
        valueInputOption='RAW', body=body).execute()

def main():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets', 'https://www.googleapis.com/auth/drive.file']
    creds = Credentials.from_service_account_file(
        'credentials/sheets-service-account.json',
        scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=creds)
    
    # Create enhanced sheets structure
    sheets = {
        'Real Estate Bot - Property Configuration': [
            'Property Types',
            'Property Features'
        ],
        'Real Estate Bot - Market Data': [
            'Market Types',
            'Location Data'
        ],
        'Real Estate Bot - Deal Analysis': [
            'Analysis Rules',
            'Repair Estimates'
        ]
    }
    
    sheet_ids = {}
    for title, worksheets in sheets.items():
        sheet_id = create_sheet(service, title, worksheets)
        sheet_ids[title] = sheet_id
        
        if 'Property Configuration' in title:
            setup_property_config(service, sheet_id)
        elif 'Market Data' in title:
            setup_market_data(service, sheet_id)
        elif 'Deal Analysis' in title:
            setup_deal_analysis(service, sheet_id)
    
    # Save sheet IDs to a file
    with open('sheet_ids.json', 'w') as f:
        json.dump(sheet_ids, f, indent=2)
    
    print("\nSheet IDs saved to sheet_ids.json")
    print("\nNext steps:")
    print("1. Update .env file with new sheet IDs")
    print("2. Share sheets with collaborators")
    print("3. Add more location data as needed")

if __name__ == '__main__':
    main()
