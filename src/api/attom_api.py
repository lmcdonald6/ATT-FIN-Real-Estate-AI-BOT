"""ATTOM API Integration for Real Estate Analysis"""
import os
import requests
from typing import Dict, Optional
from dotenv import load_dotenv
import logging

logger = logging.getLogger(__name__)
load_dotenv()

class AttomAPI:
    """Handles all ATTOM API interactions"""
    
    def __init__(self):
        self.api_key = os.getenv('ATTOM_API_KEY')
        self.base_url = os.getenv('ATTOM_API_BASE_URL', 'https://api.gateway.attomdata.com/propertyapi/v1.0.0')
        self.headers = {
            'apikey': self.api_key,
            'accept': 'application/json'
        }

    def get_property_details(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get detailed property information"""
        try:
            endpoint = f"{self.base_url}/property/detail"
            params = {
                'address': address,
                'postalcode': zipcode
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error fetching property details: {str(e)}")
            return None

    def get_avm(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get Automated Valuation Model data"""
        try:
            endpoint = f"{self.base_url}/avm/detail"
            params = {
                'address': address,
                'postalcode': zipcode
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error fetching AVM data: {str(e)}")
            return None

    def get_sales_history(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get property sales history"""
        try:
            endpoint = f"{self.base_url}/saleshistory/detail"
            params = {
                'address': address,
                'postalcode': zipcode
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error fetching sales history: {str(e)}")
            return None

    def get_market_trends(self, zipcode: str) -> Optional[Dict]:
        """Get market trends for a specific area"""
        try:
            endpoint = f"{self.base_url}/market/snapshot"
            params = {
                'postalcode': zipcode
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error fetching market trends: {str(e)}")
            return None

    def get_owner_info(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get property ownership information"""
        try:
            endpoint = f"{self.base_url}/owner/detail"
            params = {
                'address': address,
                'postalcode': zipcode
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error fetching owner info: {str(e)}")
            return None

    def get_foreclosure_info(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get foreclosure information"""
        try:
            endpoint = f"{self.base_url}/foreclosure/detail"
            params = {
                'address': address,
                'postalcode': zipcode
            }
            
            response = requests.get(endpoint, headers=self.headers, params=params)
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"Error fetching foreclosure info: {str(e)}")
            return None
