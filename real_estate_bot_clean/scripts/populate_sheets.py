"""
Script to populate Google Sheets with real market data while respecting API limits
"""
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
import json
import requests
from dotenv import load_dotenv
import os
import time
from typing import Dict, List
import pandas as pd

def get_sheets_service():
    """Initialize and return Google Sheets service."""
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        'credentials/sheets-service-account.json',
        scopes=SCOPES
    )
    return build('sheets', 'v4', credentials=creds)

def get_attom_data(zip_code: str) -> Dict:
    """Get ATTOM data for a ZIP code with rate limiting."""
    api_key = os.getenv('ATTOM_API_KEY')
    if not api_key:
        raise ValueError("ATTOM API key not found in environment variables")
    
    url = f"https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/basicprofile"
    headers = {
        'apikey': api_key,
        'accept': 'application/json'
    }
    params = {
        'postalcode': zip_code,
        'propertytype': 'SFR,CND,MFR',
        'pagesize': '10'  # Limit to 10 properties per ZIP to conserve API calls
    }
    
    response = requests.get(url, headers=headers, params=params)
    time.sleep(1)  # Rate limiting
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching ATTOM data for ZIP {zip_code}: {response.status_code}")
        return None

def analyze_market(attom_data: Dict) -> Dict:
    """Analyze market data to determine market type and price ranges."""
    if not attom_data or 'property' not in attom_data:
        return None
    
    prices = []
    for prop in attom_data['property']:
        if 'assessment' in prop and 'market' in prop['assessment']:
            prices.append(float(prop['assessment']['market']['mktTtlValue']))
    
    if not prices:
        return None
    
    avg_price = sum(prices) / len(prices)
    price_range = max(prices) - min(prices)
    
    # Determine market type based on price metrics
    if avg_price > 500000 and price_range > 300000:
        market_type = 'Hot'
    elif avg_price > 300000:
        market_type = 'Stable'
    elif price_range > 200000:
        market_type = 'Emerging'
    else:
        market_type = 'Cooling'
    
    return {
        'market_type': market_type,
        'price_min': int(min(prices)),
        'price_max': int(max(prices)),
        'avg_price': int(avg_price)
    }

def update_market_data(service, sheet_id: str, data: List[Dict]):
    """Update market data in Google Sheet."""
    values = [
        ['ZIP Code', 'City', 'State', 'Market Type', 'Price Range Min', 'Price Range Max', 'Average Price']
    ]
    
    for item in data:
        values.append([
            item['zip_code'],
            item['city'],
            item['state'],
            item['market_type'],
            str(item['price_min']),
            str(item['price_max']),
            str(item['avg_price'])
        ])
    
    range_name = 'Location Data!A1:G' + str(len(values))
    body = {'values': values}
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

def update_property_types(service, sheet_id: str):
    """Update property type mappings with real data."""
    values = [
        ['ATTOM Type', 'Redfin Type', 'Display Name', 'Min Beds', 'Min Baths', 'Min SqFt'],
        ['SFR', 'Single Family Residential', 'Single Family Home', '2', '1', '800'],
        ['CND', 'Condo/Co-op', 'Condo', '1', '1', '500'],
        ['MFR', 'Multi-Family (2-4 units)', 'Multi-Family', '2', '1', '1000'],
        ['APT', 'Apartment', 'Apartment Building', '4', '2', '2000'],
        ['MOB', 'Mobile/Manufactured Home', 'Mobile Home', '2', '1', '600'],
        ['LND', 'Vacant Land', 'Land', '0', '0', '0'],
        ['THH', 'Townhouse', 'Townhouse', '2', '1.5', '1000']
    ]
    
    range_name = 'Property Types!A1:F' + str(len(values))
    body = {'values': values}
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range=range_name,
        valueInputOption='RAW',
        body=body
    ).execute()

def main():
    load_dotenv()
    service = get_sheets_service()
    
    # Load sheet IDs
    with open('sheet_ids.json', 'r') as f:
        sheet_ids = json.load(f)
    
    # Target ZIP codes (mix of different market types)
    target_zips = [
        {'zip': '37201', 'city': 'Nashville', 'state': 'TN'},
        {'zip': '37203', 'city': 'Nashville', 'state': 'TN'},
        {'zip': '37206', 'city': 'Nashville', 'state': 'TN'},
        {'zip': '37208', 'city': 'Nashville', 'state': 'TN'},
        {'zip': '37212', 'city': 'Nashville', 'state': 'TN'}
    ]
    
    # Update property types
    print("\nUpdating property type mappings...")
    property_config_id = sheet_ids['Real Estate Bot - Property Configuration']
    update_property_types(service, property_config_id)
    
    # Collect and update market data
    print("\nCollecting market data (this may take a few minutes)...")
    market_data = []
    for location in target_zips:
        print(f"\nAnalyzing {location['city']}, {location['state']} ({location['zip']})...")
        attom_data = get_attom_data(location['zip'])
        if attom_data:
            market_info = analyze_market(attom_data)
            if market_info:
                market_data.append({
                    'zip_code': location['zip'],
                    'city': location['city'],
                    'state': location['state'],
                    **market_info
                })
    
    # Update market data sheet
    print("\nUpdating market data sheet...")
    market_data_id = sheet_ids['Real Estate Bot - Market Data']
    update_market_data(service, market_data_id, market_data)
    
    print("\nData population complete!")
    print("Note: Used only 5 ATTOM API calls out of 400 monthly limit")
    print("Next steps:")
    print("1. Review the populated data")
    print("2. Add more ZIP codes as needed")
    print("3. Adjust market type thresholds if necessary")

if __name__ == '__main__':
    main()
