"""
Real Estate Data Fetching System
Prioritizes Redfin data first, then falls back to ATTOM
"""
from typing import Dict, Optional
import aiohttp
import os
from datetime import datetime
from dotenv import load_dotenv

class RealEstateDataFetcher:
    """Fetches real estate data with source prioritization"""
    
    def __init__(self):
        load_dotenv()
        self.redfin_api_key = os.getenv('REDFIN_API_KEY')
        self.attom_api_key = os.getenv('ATTOM_API_KEY')
        
        # Define field mappings for each source
        self.redfin_fields = {
            'price', 'beds', 'baths', 'sqft', 'year_built',
            'days_on_market', 'condition_score', 'price_history',
            'maintenance_needed', 'market_trend', 'overpriced_vs_comps'
        }
        
        self.attom_fields = {
            'tax_delinquent', 'foreclosure_status', 'liens',
            'avm_value', 'owner_name', 'mailing_address',
            'length_of_residence', 'assessed_value', 'tax_history'
        }

    async def fetch_property_data(self, address: str, zipcode: str) -> Dict:
        """
        Fetch property data, prioritizing Redfin first
        """
        data = {}
        
        # Try Redfin first
        try:
            redfin_data = await self._fetch_redfin_data(address, zipcode)
            data.update(redfin_data)
        except Exception as e:
            print(f"Redfin API error: {str(e)}")
        
        # Fill in missing data with ATTOM
        try:
            # Only fetch ATTOM fields that we don't have from Redfin
            missing_fields = [f for f in self.attom_fields if f not in data]
            if missing_fields:
                attom_data = await self._fetch_attom_data(address, zipcode)
                # Only update with fields we don't already have
                for field in missing_fields:
                    if field in attom_data:
                        data[field] = attom_data[field]
        except Exception as e:
            print(f"ATTOM API error: {str(e)}")
        
        return data

    async def _fetch_redfin_data(self, address: str, zipcode: str) -> Dict:
        """Fetch data from Redfin API"""
        if not self.redfin_api_key:
            raise ValueError("Redfin API key not found")
            
        async with aiohttp.ClientSession() as session:
            headers = {
                'Authorization': f'Bearer {self.redfin_api_key}',
                'Content-Type': 'application/json'
            }
            params = {
                'address': address,
                'zipcode': zipcode
            }
            
            async with session.get(
                'https://api.redfin.com/v1/property',
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"Redfin API error: {response.status}")

    async def _fetch_attom_data(self, address: str, zipcode: str) -> Dict:
        """Fetch data from ATTOM API"""
        if not self.attom_api_key:
            raise ValueError("ATTOM API key not found")
            
        async with aiohttp.ClientSession() as session:
            headers = {
                'apikey': self.attom_api_key,
                'accept': 'application/json'
            }
            params = {
                'address': address,
                'zipcode': zipcode
            }
            
            async with session.get(
                'https://api.gateway.attomdata.com/propertyapi/v1.0.0/property/detail',
                headers=headers,
                params=params
            ) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    raise Exception(f"ATTOM API error: {response.status}")

    def get_data_freshness(self, data: Dict) -> Dict:
        """Check data freshness and source"""
        freshness = {}
        for field in data:
            if field in self.redfin_fields:
                freshness[field] = {
                    'source': 'Redfin',
                    'priority': 1
                }
            elif field in self.attom_fields:
                freshness[field] = {
                    'source': 'ATTOM',
                    'priority': 2
                }
        return freshness
