"""
Google Sheets integration for real estate AI infrastructure.
Handles data storage and configuration management.
"""
from typing import Dict, List, Optional, Any
import os
import json
import logging
import asyncio
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

class SheetsManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Load credentials and sheet IDs
        self._load_config()
        
        # Initialize service
        self.service = build(
            'sheets',
            'v4',
            credentials=self.credentials,
            cache_discovery=False
        )
        
        # Sheet ranges
        self.RANGES = {
            'market_data': 'MarketData!A:K',
            'property_data': 'PropertyData!A:M',
            'config': 'Config!A:D',
            'usage_log': 'UsageLog!A:E',
            'alerts': 'Alerts!A:C'
        }

    def _load_config(self):
        """Load Google Sheets configuration."""
        try:
            # Load credentials
            creds_path = os.getenv('SHEETS_CREDENTIALS_PATH',
                                 'credentials/sheets_cred.json')
            
            if not os.path.exists(creds_path):
                raise FileNotFoundError(
                    f"Google Sheets credentials not found at {creds_path}"
                )
            
            self.credentials = Credentials.from_service_account_file(
                creds_path,
                scopes=['https://www.googleapis.com/auth/spreadsheets']
            )
            
            # Load sheet IDs
            sheet_ids_path = 'sheet_ids.json'
            if not os.path.exists(sheet_ids_path):
                raise FileNotFoundError(
                    f"Sheet IDs configuration not found at {sheet_ids_path}"
                )
            
            with open(sheet_ids_path, 'r') as f:
                self.sheet_ids = json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading sheets configuration: {e}")
            raise

    async def get_market_data(self, zip_code: str) -> Optional[Dict]:
        """Get market data for a specific ZIP code."""
        try:
            # Prepare the query
            range_name = self.RANGES['market_data']
            result = await self._execute(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.sheet_ids['market_data'],
                    range=range_name
                )
            )
            
            if not result.get('values'):
                return None
            
            # Find row with matching ZIP code
            headers = result['values'][0]
            for row in result['values'][1:]:
                if row[0] == zip_code:  # ZIP code is in first column
                    return dict(zip(headers, row))
            
            return None
        except Exception as e:
            self.logger.error(f"Error getting market data for {zip_code}: {e}")
            raise

    async def update_market_data(self, zip_code: str, data: Dict):
        """Update market data for a specific ZIP code."""
        try:
            # First get existing data to find row
            range_name = self.RANGES['market_data']
            result = await self._execute(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.sheet_ids['market_data'],
                    range=range_name
                )
            )
            
            if not result.get('values'):
                # Create new sheet with headers if empty
                headers = [
                    'zip_code', 'median_price', 'price_trend',
                    'days_on_market', 'inventory_level', 'sales_velocity',
                    'price_per_sqft', 'distress_ratio', 'overall_score',
                    'last_updated'
                ]
                values = [headers]
            else:
                values = result['values']
                headers = values[0]
            
            # Find or create row for ZIP code
            row_index = None
            for i, row in enumerate(values):
                if row[0] == zip_code:
                    row_index = i
                    break
            
            # Prepare new row data
            new_row = [data.get(header.lower(), '') for header in headers]
            new_row[0] = zip_code  # Ensure ZIP code is set
            
            if row_index is not None:
                # Update existing row
                range_name = f"MarketData!A{row_index + 1}"
                body = {'values': [new_row]}
                await self._execute(
                    self.service.spreadsheets().values().update(
                        spreadsheetId=self.sheet_ids['market_data'],
                        range=range_name,
                        valueInputOption='USER_ENTERED',
                        body=body
                    )
                )
            else:
                # Append new row
                body = {'values': [new_row]}
                await self._execute(
                    self.service.spreadsheets().values().append(
                        spreadsheetId=self.sheet_ids['market_data'],
                        range=self.RANGES['market_data'],
                        valueInputOption='USER_ENTERED',
                        body=body
                    )
                )
        except Exception as e:
            self.logger.error(
                f"Error updating market data for {zip_code}: {e}"
            )
            raise

    async def get_hot_markets(self) -> List[str]:
        """Get list of hot market ZIP codes."""
        try:
            result = await self._execute(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.sheet_ids['market_data'],
                    range=self.RANGES['market_data']
                )
            )
            
            if not result.get('values'):
                return []
            
            hot_markets = []
            headers = result['values'][0]
            score_index = headers.index('overall_score')
            zip_index = headers.index('zip_code')
            
            for row in result['values'][1:]:
                if float(row[score_index]) >= 80:  # Consider 80+ as hot market
                    hot_markets.append(row[zip_index])
            
            return hot_markets
        except Exception as e:
            self.logger.error(f"Error getting hot markets: {e}")
            raise

    async def get_market_config(self) -> Dict:
        """Get market configuration data."""
        try:
            result = await self._execute(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.sheet_ids['config'],
                    range='MarketConfig!A:D'
                )
            )
            
            if not result.get('values'):
                return {}
            
            config = {}
            headers = result['values'][0]
            for row in result['values'][1:]:
                market_type = row[0]
                config[market_type] = {
                    'price_change': float(row[1]),
                    'dom': int(row[2]),
                    'inventory': float(row[3])
                }
            
            return config
        except Exception as e:
            self.logger.error(f"Error getting market config: {e}")
            raise

    async def get_deal_config(self) -> Dict:
        """Get deal analysis configuration."""
        try:
            result = await self._execute(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.sheet_ids['config'],
                    range='DealConfig!A:D'
                )
            )
            
            if not result.get('values'):
                return {}
            
            config = {}
            headers = result['values'][0]
            for row in result['values'][1:]:
                deal_type = row[0]
                config[deal_type] = {
                    key.lower(): float(value)
                    for key, value in zip(headers[1:], row[1:])
                }
            
            return config
        except Exception as e:
            self.logger.error(f"Error getting deal config: {e}")
            raise

    async def get_comps(self, zip_code: str, bedrooms: int,
                       square_feet: float) -> List[Dict]:
        """Get comparable properties from historical data."""
        try:
            result = await self._execute(
                self.service.spreadsheets().values().get(
                    spreadsheetId=self.sheet_ids['property_data'],
                    range=self.RANGES['property_data']
                )
            )
            
            if not result.get('values'):
                return []
            
            headers = result['values'][0]
            comps = []
            
            # Find properties in same ZIP code with similar characteristics
            for row in result['values'][1:]:
                data = dict(zip(headers, row))
                if (data['zip_code'] == zip_code and
                    int(data['bedrooms']) == bedrooms and
                    0.8 <= float(data['square_feet']) / square_feet <= 1.2):
                    comps.append(data)
            
            return comps[:10]  # Return top 10 comps
        except Exception as e:
            self.logger.error(f"Error getting comps: {e}")
            raise

    async def update_usage_log(self, usage_data: Dict):
        """Log API usage data."""
        try:
            row = [
                usage_data['timestamp'],
                usage_data['calls_today'],
                usage_data['calls_this_month'],
                usage_data['remaining_calls'],
                usage_data['estimated_cost']
            ]
            
            body = {'values': [row]}
            await self._execute(
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.sheet_ids['usage_log'],
                    range=self.RANGES['usage_log'],
                    valueInputOption='USER_ENTERED',
                    body=body
                )
            )
        except Exception as e:
            self.logger.error(f"Error updating usage log: {e}")
            raise

    async def log_alerts(self, alert_data: Dict):
        """Log system alerts."""
        try:
            row = [
                alert_data['timestamp'],
                len(alert_data['alerts']),
                '\n'.join(alert_data['alerts'])
            ]
            
            body = {'values': [row]}
            await self._execute(
                self.service.spreadsheets().values().append(
                    spreadsheetId=self.sheet_ids['alerts'],
                    range=self.RANGES['alerts'],
                    valueInputOption='USER_ENTERED',
                    body=body
                )
            )
        except Exception as e:
            self.logger.error(f"Error logging alerts: {e}")
            raise

    async def _execute(self, request):
        """Execute a Google Sheets API request."""
        try:
            return await asyncio.get_event_loop().run_in_executor(
                self._executor,
                request.execute
            )
        except HttpError as e:
            if e.resp.status == 429:  # Rate limit exceeded
                self.logger.warning("Rate limit hit, implementing backoff...")
                await asyncio.sleep(5)  # Simple backoff
                return await self._execute(request)
            raise

    def __del__(self):
        """Cleanup on deletion."""
        self._executor.shutdown(wait=False)
