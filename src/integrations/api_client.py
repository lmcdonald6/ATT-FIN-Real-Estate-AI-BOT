from typing import Dict, Optional
import aiohttp
import logging
import os
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from datetime import datetime

class APIClient:
    """Unified API client for ATTOM and Redfin data"""
    
    def __init__(self):
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        
        # API configurations
        self.attom_api_key = os.getenv('ATTOM_API_KEY')
        self.attom_base_url = os.getenv('ATTOM_API_BASE_URL')
        self.redfin_base_url = "https://www.redfin.com/stingray/do/location-autocomplete"
        
        if not self.attom_api_key:
            raise ValueError("ATTOM API key not found in environment variables")
    
    async def get_property_data(self, address: str, zipcode: str) -> Dict:
        """Get property data, prioritizing Redfin for free data"""
        try:
            # First try Redfin
            redfin_data = await self._get_redfin_data(address, zipcode)
            
            # Get additional data from ATTOM if needed
            attom_data = await self._get_attom_property_details(address, zipcode)
            
            # Combine data, prioritizing Redfin for overlapping fields
            combined_data = {**attom_data, **redfin_data}
            
            return combined_data
            
        except Exception as e:
            self.logger.error(f"Error fetching property data: {str(e)}")
            raise
    
    async def _get_redfin_data(self, address: str, zipcode: str) -> Dict:
        """Get property data from Redfin"""
        try:
            async with aiohttp.ClientSession() as session:
                params = {
                    'location': f"{address} {zipcode}",
                    'start': 0,
                    'count': 1
                }
                
                async with session.get(self.redfin_base_url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_redfin_response(data)
                    else:
                        self.logger.warning(f"Redfin API returned status {response.status}")
                        return {}
                        
        except Exception as e:
            self.logger.error(f"Error fetching Redfin data: {str(e)}")
            return {}
    
    async def _get_attom_property_details(self, address: str, zipcode: str) -> Dict:
        """Get property details from ATTOM"""
        try:
            headers = {
                'apikey': self.attom_api_key,
                'accept': 'application/json'
            }
            
            endpoint = f"{self.attom_base_url}/property/detail"
            params = {
                'address': address,
                'zipcode': zipcode
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_attom_response(data)
                    else:
                        self.logger.error(f"ATTOM API returned status {response.status}")
                        raise Exception(f"ATTOM API error: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Error fetching ATTOM data: {str(e)}")
            raise
    
    async def get_market_data(self, zipcode: str) -> Dict:
        """Get market analysis data"""
        try:
            headers = {
                'apikey': self.attom_api_key,
                'accept': 'application/json'
            }
            
            endpoint = f"{self.attom_base_url}/market/snapshot"
            params = {'zipcode': zipcode}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_market_data(data)
                    else:
                        raise Exception(f"Market data API error: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Error fetching market data: {str(e)}")
            raise
    
    async def get_owner_info(self, address: str, zipcode: str) -> Dict:
        """Get owner information from ATTOM"""
        try:
            headers = {
                'apikey': self.attom_api_key,
                'accept': 'application/json'
            }
            
            endpoint = f"{self.attom_base_url}/property/expandedprofile"
            params = {
                'address': address,
                'zipcode': zipcode
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=headers, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        return self._parse_owner_info(data)
                    else:
                        raise Exception(f"Owner info API error: {response.status}")
                        
        except Exception as e:
            self.logger.error(f"Error fetching owner info: {str(e)}")
            raise
    
    def _parse_redfin_response(self, data: Dict) -> Dict:
        """Parse Redfin API response"""
        try:
            property_data = {}
            if 'payload' in data:
                payload = data['payload']
                property_data = {
                    'price': payload.get('price', 0),
                    'beds': payload.get('beds', 0),
                    'baths': payload.get('baths', 0),
                    'sqft': payload.get('sqft', 0),
                    'year_built': payload.get('yearBuilt', 0),
                    'lot_size': payload.get('lotSize', 0),
                    'price_per_sqft': payload.get('pricePerSqft', 0),
                    'days_on_market': payload.get('daysOnMarket', 0),
                    'property_type': payload.get('propertyType', ''),
                    'last_sold_date': payload.get('lastSoldDate', ''),
                    'last_sold_price': payload.get('lastSoldPrice', 0)
                }
            return property_data
        except Exception as e:
            self.logger.error(f"Error parsing Redfin data: {str(e)}")
            return {}
    
    def _parse_attom_response(self, data: Dict) -> Dict:
        """Parse ATTOM property details response"""
        try:
            property_data = {}
            if 'property' in data:
                prop = data['property'][0]
                property_data = {
                    'avm_value': prop.get('avm', {}).get('amount', 0),
                    'tax_assessment': prop.get('assessment', {}).get('assessed', 0),
                    'tax_year': prop.get('assessment', {}).get('tax_year', 0),
                    'legal_description': prop.get('summary', {}).get('legal1', ''),
                    'zoning': prop.get('summary', {}).get('zoning', ''),
                    'distressed': prop.get('summary', {}).get('distressed', False),
                    'foreclosure_status': prop.get('summary', {}).get('foreclosure', ''),
                    'owner_occupied': prop.get('summary', {}).get('ownerOccupied', False)
                }
            return property_data
        except Exception as e:
            self.logger.error(f"Error parsing ATTOM data: {str(e)}")
            return {}
    
    def _parse_market_data(self, data: Dict) -> Dict:
        """Parse market analysis data"""
        try:
            market_data = {}
            if 'market' in data:
                market = data['market']
                market_data = {
                    'median_price': market.get('medianPrice', 0),
                    'price_trend': market.get('priceTrend', ''),
                    'days_on_market': market.get('averageDom', 0),
                    'inventory_level': market.get('inventoryLevel', 0),
                    'market_action_index': market.get('marketActionIndex', 0),
                    'price_per_sqft': market.get('medianPricePerSqft', 0),
                    'price_appreciation': market.get('appreciation', {}).get('5year', 0),
                    'rental_yield': market.get('rentalYield', 0)
                }
            return market_data
        except Exception as e:
            self.logger.error(f"Error parsing market data: {str(e)}")
            return {}
    
    def _parse_owner_info(self, data: Dict) -> Dict:
        """Parse owner information"""
        try:
            owner_data = {}
            if 'owner' in data:
                owner = data['owner']
                owner_data = {
                    'owner_name': owner.get('name', ''),
                    'mailing_address': owner.get('mailingAddress', ''),
                    'owner_type': owner.get('ownerType', ''),
                    'ownership_length': owner.get('ownershipLength', 0),
                    'last_sale_date': owner.get('lastSaleDate', ''),
                    'last_sale_price': owner.get('lastSalePrice', 0),
                    'estimated_equity': owner.get('estimatedEquity', 0)
                }
            return owner_data
        except Exception as e:
            self.logger.error(f"Error parsing owner info: {str(e)}")
            return {}
