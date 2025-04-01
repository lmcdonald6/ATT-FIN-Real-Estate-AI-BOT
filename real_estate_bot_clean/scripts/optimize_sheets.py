"""
Script to optimize Google Sheets structure for maximum usability and functionality
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

def setup_market_intelligence(service, sheet_id):
    """Set up enhanced market intelligence data structure."""
    # Market Types with Detailed Criteria
    values = [
        ['Market Type', 'Description', 'Base Multiplier', 'API Priority', 'Update Frequency', 'Cache Duration (hours)'],
        ['Hot', 'High demand, rapid appreciation', '1.2', 'High (Always use ATTOM)', 'Weekly', '24'],
        ['Growing', 'Strong appreciation trends', '1.1', 'Medium (Use ATTOM if available)', 'Weekly', '48'],
        ['Stable', 'Consistent market conditions', '1.0', 'Low (Selective ATTOM use)', 'Bi-weekly', '72'],
        ['Emerging', 'Up-and-coming area', '0.9', 'Low (Mock data preferred)', 'Monthly', '96'],
        ['Cooling', 'Slowing market conditions', '0.85', 'Very Low (Mock data only)', 'Monthly', '120']
    ]
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Market Types!A1:F6',
        valueInputOption='RAW',
        body={'values': values}
    ).execute()
    
    # Enhanced Location Data
    values = [
        ['ZIP Code', 'City', 'State', 'Market Type', 'Price Range', 'Preferred Property Types', 'Investment Strategy', 'Local Factors'],
        ['37201', 'Nashville', 'TN', 'Hot', '300k-800k', 'SFR, MFR', 'Fix & Flip', 'Downtown proximity, Entertainment district'],
        ['37203', 'Nashville', 'TN', 'Growing', '250k-600k', 'SFR, Condos', 'BRRRR', 'University area, Young professionals'],
        ['37206', 'Nashville', 'TN', 'Emerging', '200k-450k', 'SFR, Duplex', 'Buy & Hold', 'Gentrification, Art district']
    ]
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Location Data!A1:H4',
        valueInputOption='RAW',
        body={'values': values}
    ).execute()

def setup_property_config(service, sheet_id):
    """Set up enhanced property configuration."""
    # Property Types with Advanced Mapping
    values = [
        ['ATTOM Type', 'Redfin Type', 'Min Beds', 'Min Baths', 'Min SqFt', 'Target Markets', 'Investment Strategy', 'Risk Level'],
        ['SFR', 'Single Family', '3', '2', '1200', 'Hot, Growing', 'Fix & Flip', 'Low'],
        ['MFR', 'Multi-Family', '2', '1', '800', 'Growing, Emerging', 'BRRRR', 'Medium'],
        ['CND', 'Condo', '1', '1', '600', 'Hot', 'Buy & Hold', 'Low'],
        ['DPX', 'Duplex', '2', '1', '1000', 'Emerging', 'BRRRR', 'Medium'],
        ['TWN', 'Townhouse', '2', '1.5', '1000', 'Stable', 'Buy & Hold', 'Low']
    ]
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Property Types!A1:H6',
        valueInputOption='RAW',
        body={'values': values}
    ).execute()
    
    # Deal Scoring Criteria
    values = [
        ['Criteria', 'Weight', 'Scoring Rules', 'Notes'],
        ['ROI', '40', '>=30%: 40pts, >=20%: 30pts, >=15%: 20pts', 'Primary factor'],
        ['Market Type', '20', 'Hot: 20pts, Growing: 15pts, Others: 10pts', 'Market potential'],
        ['Property Condition', '15', 'Excellent: 15pts, Good: 10pts, Fair: 5pts', 'Repair needs'],
        ['Location Quality', '15', 'Prime: 15pts, Good: 10pts, Average: 5pts', 'Area desirability'],
        ['Seller Motivation', '10', 'High: 10pts, Medium: 5pts, Low: 0pts', 'Negotiation potential']
    ]
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Scoring Criteria!A1:D6',
        valueInputOption='RAW',
        body={'values': values}
    ).execute()

def setup_deal_analysis(service, sheet_id):
    """Set up enhanced deal analysis configuration."""
    # Market-Specific ROI Rules
    values = [
        ['Market Type', 'Min ROI', 'Target ROI', 'Max Purchase Multiple', 'Hold Period', 'Exit Strategy'],
        ['Hot', '15%', '25%', '0.75', '3-6 months', 'Wholesale or Fix & Flip'],
        ['Growing', '20%', '30%', '0.7', '6-12 months', 'Fix & Flip or BRRRR'],
        ['Stable', '25%', '35%', '0.65', '12+ months', 'Buy & Hold'],
        ['Emerging', '30%', '40%', '0.6', '18+ months', 'BRRRR'],
        ['Cooling', '35%', '45%', '0.55', '24+ months', 'Buy & Hold']
    ]
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='ROI Rules!A1:F6',
        valueInputOption='RAW',
        body={'values': values}
    ).execute()
    
    # Enhanced Repair Calculator
    values = [
        ['Category', 'Base Cost', 'Unit', 'Quality Level', 'Market Adjustments', 'Typical Timeline'],
        ['Roof', '8000', 'per job', 'Standard: 1x, Premium: 1.3x', 'Hot: +20%, Cooling: -10%', '1-2 weeks'],
        ['HVAC', '6000', 'per unit', 'Standard: 1x, Premium: 1.4x', 'Hot: +15%, Cooling: -5%', '2-3 days'],
        ['Kitchen', '15000', 'per room', 'Standard: 1x, Luxury: 1.5x', 'Hot: +25%, Cooling: -15%', '2-3 weeks'],
        ['Bath', '8000', 'per room', 'Standard: 1x, Luxury: 1.4x', 'Hot: +20%, Cooling: -10%', '1-2 weeks']
    ]
    service.spreadsheets().values().update(
        spreadsheetId=sheet_id,
        range='Repair Calculator!A1:F5',
        valueInputOption='RAW',
        body={'values': values}
    ).execute()

def main():
    SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
    creds = Credentials.from_service_account_file(
        'credentials/sheets-service-account.json',
        scopes=SCOPES
    )
    service = build('sheets', 'v4', credentials=creds)
    
    # Create enhanced sheets structure
    sheets = {
        'Real Estate Bot - Market Intelligence': [
            'Market Types',
            'Location Data'
        ],
        'Real Estate Bot - Property Configuration': [
            'Property Types',
            'Scoring Criteria'
        ],
        'Real Estate Bot - Deal Analysis': [
            'ROI Rules',
            'Repair Calculator'
        ]
    }
    
    sheet_ids = {}
    for title, worksheets in sheets.items():
        sheet_id = create_sheet(service, title, worksheets)
        sheet_ids[title] = sheet_id
        
        if 'Market Intelligence' in title:
            setup_market_intelligence(service, sheet_id)
        elif 'Property Configuration' in title:
            setup_property_config(service, sheet_id)
        elif 'Deal Analysis' in title:
            setup_deal_analysis(service, sheet_id)
    
    # Save sheet IDs
    with open('sheet_ids.json', 'w') as f:
        json.dump(sheet_ids, f, indent=2)
    
    print("\nEnhanced sheet structure created!")
    print("\nKey Improvements:")
    print("1. Market Intelligence:")
    print("   - Added 5 market types with specific API priorities")
    print("   - Enhanced location data with investment strategies")
    print("   - Dynamic cache durations based on market type")
    print("\n2. Property Configuration:")
    print("   - Advanced property type mapping with risk levels")
    print("   - Comprehensive deal scoring criteria")
    print("   - Market-specific investment strategies")
    print("\n3. Deal Analysis:")
    print("   - Market-specific ROI rules and hold periods")
    print("   - Enhanced repair calculator with quality levels")
    print("   - Timeline estimates for renovations")

if __name__ == '__main__':
    main()
