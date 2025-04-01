"""
Google Sheets integration for real estate data management.
Handles property mappings, location data, and price multipliers.
"""
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from typing import Dict, List, Optional
import logging
import json
import os

logger = logging.getLogger(__name__)

class SheetsManager:
    def __init__(self, credentials_path: str):
        self.SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
        self.credentials_path = credentials_path
        self.sheets_service = None
        self._initialize_service()
        
        # Sheet IDs will be configured via environment variables
        self.property_mappings_sheet = os.getenv('PROPERTY_MAPPINGS_SHEET_ID')
        self.location_data_sheet = os.getenv('LOCATION_DATA_SHEET_ID')
        self.price_multipliers_sheet = os.getenv('PRICE_MULTIPLIERS_SHEET_ID')
        
    def _initialize_service(self):
        """Initialize Google Sheets service with credentials"""
        try:
            creds = Credentials.from_service_account_file(
                self.credentials_path, scopes=self.SCOPES
            )
            self.sheets_service = build('sheets', 'v4', credentials=creds)
            logger.info("Successfully initialized Google Sheets service")
        except Exception as e:
            logger.error(f"Failed to initialize Google Sheets service: {str(e)}")
            raise

    def get_property_mappings(self) -> Dict:
        """Fetch property type mappings from Google Sheets"""
        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.property_mappings_sheet,
                range='PropertyMappings!A2:B'
            ).execute()
            
            mappings = {}
            for row in result.get('values', []):
                if len(row) >= 2:
                    mappings[row[0]] = row[1]
            return mappings
            
        except Exception as e:
            logger.error(f"Error fetching property mappings: {str(e)}")
            return {}

    def get_location_data(self, zip_code: str = None) -> Dict:
        """Fetch location data (ZIP codes, cities, states)"""
        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.location_data_sheet,
                range='LocationData!A2:D'
            ).execute()
            
            if zip_code:
                for row in result.get('values', []):
                    if row[0] == zip_code:
                        return {
                            'zip_code': row[0],
                            'city': row[1],
                            'state': row[2],
                            'market_type': row[3]
                        }
                return {}
            
            locations = []
            for row in result.get('values', []):
                if len(row) >= 4:
                    locations.append({
                        'zip_code': row[0],
                        'city': row[1],
                        'state': row[2],
                        'market_type': row[3]
                    })
            return {'locations': locations}
            
        except Exception as e:
            logger.error(f"Error fetching location data: {str(e)}")
            return {}

    def get_price_multipliers(self, market_type: str = None) -> Dict:
        """Fetch price multipliers by area/market type"""
        try:
            result = self.sheets_service.spreadsheets().values().get(
                spreadsheetId=self.price_multipliers_sheet,
                range='PriceMultipliers!A2:C'
            ).execute()
            
            multipliers = {}
            for row in result.get('values', []):
                if len(row) >= 3:
                    multipliers[row[0]] = {
                        'base_multiplier': float(row[1]),
                        'market_adjustment': float(row[2])
                    }
            
            if market_type:
                return multipliers.get(market_type, {})
            return multipliers
            
        except Exception as e:
            logger.error(f"Error fetching price multipliers: {str(e)}")
            return {}
