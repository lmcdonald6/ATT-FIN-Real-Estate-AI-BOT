"""Data Collector for Real Estate AI Bot"""
import requests
import json
from bs4 import BeautifulSoup
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

class RealEstateDataCollector:
    """Collects and structures real estate data from ATTOM and Redfin"""
    
    def __init__(self):
        self.attom_api_key = os.getenv('ATTOM_API_KEY')
        self.attom_base_url = "https://api.gateway.attomdata.com/propertyapi/v1.0.0"
        self.headers = {
            'apikey': self.attom_api_key,
            'accept': 'application/json'
        }
        
    def get_property_data(self, address: str, zip_code: str) -> Dict:
        """Get comprehensive property data"""
        try:
            # Collect ATTOM data
            attom_data = self._get_attom_data(address, zip_code)
            
            # Collect Redfin data
            redfin_data = self._get_redfin_data(address, zip_code)
            
            # Combine and structure the data
            return self._structure_property_data(attom_data, redfin_data)
            
        except Exception as e:
            logger.error(f"Error collecting property data: {str(e)}")
            return {}
            
    def _get_attom_data(self, address: str, zip_code: str) -> Dict:
        """Fetch data from ATTOM API"""
        try:
            # Basic property details
            endpoint = f"{self.attom_base_url}/property/detail"
            params = {
                'address': address,
                'zipcode': zip_code
            }
            
            response = requests.get(
                endpoint,
                headers=self.headers,
                params=params
            )
            response.raise_for_status()
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"ATTOM API error: {str(e)}")
            return {}
            
    def _get_redfin_data(self, address: str, zip_code: str) -> Dict:
        """Scrape data from Redfin"""
        try:
            # Format address for Redfin URL
            formatted_address = address.replace(' ', '-').lower()
            url = f"https://www.redfin.com/zipcode/{zip_code}/address/{formatted_address}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            return self._parse_redfin_data(soup)
            
        except requests.RequestException as e:
            logger.error(f"Redfin scraping error: {str(e)}")
            return {}
            
    def _parse_redfin_data(self, soup: BeautifulSoup) -> Dict:
        """Parse Redfin HTML data"""
        data = {
            'price': self._extract_text(soup, '.price'),
            'beds': self._extract_text(soup, '.beds'),
            'baths': self._extract_text(soup, '.baths'),
            'sqft': self._extract_text(soup, '.sqft'),
            'status': self._extract_text(soup, '.status'),
            'description': self._extract_text(soup, '.description')
        }
        return data
        
    def _extract_text(self, soup: BeautifulSoup, selector: str) -> str:
        """Extract text from BeautifulSoup element"""
        element = soup.select_one(selector)
        return element.text.strip() if element else ''
        
    def _structure_property_data(self, attom_data: Dict, redfin_data: Dict) -> Dict:
        """Structure combined property data for AI processing"""
        return {
            'property_details': {
                'address': attom_data.get('address', {}),
                'basic_info': {
                    'beds': redfin_data.get('beds'),
                    'baths': redfin_data.get('baths'),
                    'sqft': redfin_data.get('sqft'),
                    'status': redfin_data.get('status')
                },
                'description': redfin_data.get('description')
            },
            'valuation': {
                'current_value': attom_data.get('assessment', {}).get('value'),
                'market_value': redfin_data.get('price')
            },
            'property_history': attom_data.get('saleHistory', []),
            'market_data': {
                'days_on_market': attom_data.get('market', {}).get('daysOnMarket'),
                'price_history': attom_data.get('market', {}).get('priceHistory', [])
            }
        }
