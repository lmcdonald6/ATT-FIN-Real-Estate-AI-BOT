"""
Setup script for creating and initializing Google Sheets for real estate data.
Implements the hybrid data approach with mock Redfin data and ATTOM API integration.
"""
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import os
from dotenv import load_dotenv

def create_sheet(service, title, sheets):
    """Create a new Google Sheet with given title and specified worksheets."""
    sheet_metadata = {
        'properties': {'title': title},
        'sheets': [{'properties': {'title': name}} for name in sheets]
    }
    sheet = service.spreadsheets().create(body=sheet_metadata).execute()
    return sheet['spreadsheetId']

def setup_property_mappings(service, sheet_id):
    """Initialize property type mappings sheet with ATTOM and Redfin mappings."""
    values = [
        ['ATTOM_TYPE', 'REDFIN_TYPE', 'STANDARDIZED_TYPE'],
        ['SFR', 'Single Family Residential', 'Single Family'],
        ['APT', 'Apartment', 'Apartment'],
        ['CONDO', 'Condominium', 'Condominium'],
        ['DUPLEX', 'Multi-Family (2)', 'Multi-Family'],
        ['TRIPLEX', 'Multi-Family (3)', 'Multi-Family'],
        ['QUADPLEX', 'Multi-Family (4)', 'Multi-Family'],
        ['LOT', 'Land', 'Land'],
        ['MOBILE', 'Mobile/Manufactured', 'Mobile Home']
    ]
    body = {'values': values}
    range_name = 'PropertyTypes!A1'  # Using the correct sheet name
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

def setup_location_data(service, sheet_id):
    """Initialize location data sheet with focus on nationwide coverage."""
    values = [
        ['ZIP_CODE', 'CITY', 'STATE', 'MARKET_TYPE', 'DATA_SOURCE'],
        ['35020', 'Bessemer', 'AL', 'emerging', 'hybrid'],
        ['35215', 'Center Point', 'AL', 'stable', 'mock'],
        ['35217', 'Birmingham', 'AL', 'growing', 'attom'],
        ['35218', 'Birmingham', 'AL', 'emerging', 'mock'],
        ['35221', 'Birmingham', 'AL', 'stable', 'hybrid']
    ]
    body = {'values': values}
    range_name = 'Locations!A1'  # Using the correct sheet name
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

def setup_price_multipliers(service, sheet_id):
    """Initialize price multipliers sheet with market-specific adjustments."""
    values = [
        ['MARKET_TYPE', 'BASE_MULTIPLIER', 'MARKET_ADJUSTMENT', 'LAST_UPDATED'],
        ['emerging', '0.85', '0.05', '2025-03-15'],
        ['stable', '0.90', '0.02', '2025-03-15'],
        ['growing', '0.95', '0.03', '2025-03-15'],
        ['hot', '1.00', '0.04', '2025-03-15']
    ]
    body = {'values': values}
    range_name = 'Multipliers!A1'  # Using the correct sheet name
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

def main():
    # Initialize Google Sheets API
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        'credentials/sheets-service-account.json',
        scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=creds)
    
    # Create sheets with predefined worksheets
    sheets = {
        'property_mappings': ('Real Estate Bot - Property Mappings', ['PropertyTypes']),
        'location_data': ('Real Estate Bot - Location Data', ['Locations']),
        'price_multipliers': ('Real Estate Bot - Price Multipliers', ['Multipliers'])
    }
    
    sheet_ids = {}
    for key, (title, worksheets) in sheets.items():
        print(f"Creating {title}...")
        sheet_ids[key] = create_sheet(service, title, worksheets)
        
    # Initialize sheets with data
    print("Setting up property mappings...")
    setup_property_mappings(service, sheet_ids['property_mappings'])
    
    print("Setting up location data...")
    setup_location_data(service, sheet_ids['location_data'])
    
    print("Setting up price multipliers...")
    setup_price_multipliers(service, sheet_ids['price_multipliers'])
    
    # Print sheet IDs for .env configuration
    print("\nAdd these IDs to your .env file:")
    print(f"PROPERTY_MAPPINGS_SHEET_ID={sheet_ids['property_mappings']}")
    print(f"LOCATION_DATA_SHEET_ID={sheet_ids['location_data']}")
    print(f"PRICE_MULTIPLIERS_SHEET_ID={sheet_ids['price_multipliers']}")

if __name__ == '__main__':
    main()
