"""ATTOM API Integration Module"""
from typing import Dict, List, Optional
import os
import requests
from datetime import datetime
from dotenv import load_dotenv

class AttomAPI:
    """ATTOM API Client for Real Estate Data"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv('ATTOM_API_KEY')
        self.base_url = os.getenv('ATTOM_API_BASE_URL')
        self.session = requests.Session()
        self.session.headers.update({
            'apikey': self.api_key,
            'accept': 'application/json'
        })
    
    def get_property_details(self, address: str, zipcode: str) -> Dict:
        """Get detailed property information"""
        endpoint = f"{self.base_url}/property/detail"
        params = {
            'address': address,
            'zipcode': zipcode
        }
        response = self._make_request('GET', endpoint, params)
        return self._format_property_details(response)
    
    def get_property_value(self, address: str, zipcode: str) -> Dict:
        """Get property valuation details"""
        endpoint = f"{self.base_url}/property/value"
        params = {
            'address': address,
            'zipcode': zipcode
        }
        response = self._make_request('GET', endpoint, params)
        return self._format_property_value(response)
    
    def get_distressed_info(self, address: str, zipcode: str) -> Dict:
        """Get distressed property information"""
        endpoint = f"{self.base_url}/property/foreclosure"
        params = {
            'address': address,
            'zipcode': zipcode
        }
        response = self._make_request('GET', endpoint, params)
        return self._format_distressed_info(response)
    
    def get_owner_info(self, address: str, zipcode: str) -> Dict:
        """Get property ownership information"""
        endpoint = f"{self.base_url}/property/owner"
        params = {
            'address': address,
            'zipcode': zipcode
        }
        response = self._make_request('GET', endpoint, params)
        return self._format_owner_info(response)
    
    def get_market_stats(self, zipcode: str) -> Dict:
        """Get market statistics for an area"""
        endpoint = f"{self.base_url}/market/snapshot"
        params = {
            'zipcode': zipcode
        }
        response = self._make_request('GET', endpoint, params)
        return self._format_market_stats(response)
    
    def _make_request(self, method: str, endpoint: str, params: Dict) -> Dict:
        """Make API request with error handling"""
        try:
            response = self.session.request(method, endpoint, params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                'error': str(e),
                'status': 'error',
                'timestamp': datetime.now().isoformat()
            }
    
    def _format_property_details(self, response: Dict) -> Dict:
        """Format property details response"""
        if response.get('status') == 'error':
            return response
            
        return {
            'property_value': {
                'estimated_value': response.get('avm', {}).get('value'),
                'confidence_score': response.get('avm', {}).get('confidence'),
                'price_trend': response.get('market', {}).get('trend'),
                'last_sale': response.get('sale', {}).get('amount')
            },
            'property_details': {
                'beds': response.get('building', {}).get('beds'),
                'baths': response.get('building', {}).get('baths'),
                'sqft': response.get('building', {}).get('size'),
                'year_built': response.get('summary', {}).get('yearBuilt'),
                'lot_size': response.get('lot', {}).get('size'),
                'property_type': response.get('summary', {}).get('proptype')
            },
            'tax_assessment': {
                'assessed_value': response.get('assessment', {}).get('value'),
                'tax_year': response.get('assessment', {}).get('year'),
                'tax_amount': response.get('tax', {}).get('amount'),
                'tax_status': 'Delinquent' if response.get('tax', {}).get('delinquent') else 'Current'
            }
        }
    
    def _format_property_value(self, response: Dict) -> Dict:
        """Format property value response"""
        if response.get('status') == 'error':
            return response
            
        return {
            'value_analysis': {
                'estimated_value': response.get('value'),
                'confidence_score': response.get('confidence'),
                'forecast_12m': response.get('forecast', {}).get('12month'),
                'value_change': response.get('historical', {}).get('lastYear')
            },
            'value_components': {
                'land_value': response.get('components', {}).get('land'),
                'improvement_value': response.get('components', {}).get('improvement'),
                'total_value': response.get('components', {}).get('total')
            },
            'market_position': {
                'percentile': response.get('market', {}).get('percentile'),
                'trend': response.get('market', {}).get('trend'),
                'days_on_market': response.get('market', {}).get('dom')
            }
        }
    
    def _format_distressed_info(self, response: Dict) -> Dict:
        """Format distressed property information"""
        if response.get('status') == 'error':
            return response
            
        return {
            'foreclosure_status': {
                'status': response.get('foreclosure', {}).get('status'),
                'stage': response.get('foreclosure', {}).get('stage'),
                'auction_date': response.get('auction', {}).get('date'),
                'default_amount': response.get('default', {}).get('amount')
            },
            'liens_bankruptcy': {
                'total_liens': len(response.get('liens', [])),
                'lien_amount': sum(lien.get('amount', 0) for lien in response.get('liens', [])),
                'bankruptcy_status': response.get('bankruptcy', {}).get('status')
            },
            'timeline': [
                {
                    'date': event.get('date'),
                    'type': event.get('type'),
                    'description': event.get('description')
                }
                for event in response.get('timeline', [])
            ]
        }
    
    def _format_owner_info(self, response: Dict) -> Dict:
        """Format owner information"""
        if response.get('status') == 'error':
            return response
            
        return {
            'owner_info': {
                'name': response.get('owner', {}).get('name'),
                'type': response.get('owner', {}).get('type'),
                'occupied': response.get('occupancy', {}).get('owner_occupied'),
                'acquisition_date': response.get('owner', {}).get('acquisition_date')
            },
            'contact_info': {
                'mailing_address': response.get('owner', {}).get('mailing_address'),
                'phone': response.get('owner', {}).get('phone'),
                'email': response.get('owner', {}).get('email')
            },
            'portfolio': {
                'other_properties': response.get('portfolio', {}).get('count'),
                'estimated_equity': response.get('portfolio', {}).get('total_equity'),
                'total_value': response.get('portfolio', {}).get('total_value')
            }
        }
    
    def _format_market_stats(self, response: Dict) -> Dict:
        """Format market statistics"""
        if response.get('status') == 'error':
            return response
            
        return {
            'price_trends': {
                'median_price': response.get('price', {}).get('median'),
                'price_change': response.get('price', {}).get('change'),
                'forecast': response.get('price', {}).get('forecast')
            },
            'market_metrics': {
                'inventory': response.get('inventory', {}).get('active'),
                'days_on_market': response.get('market', {}).get('dom'),
                'price_reductions': response.get('market', {}).get('price_reduced_ratio')
            },
            'sales_metrics': {
                'monthly_sales': response.get('sales', {}).get('monthly'),
                'price_per_sqft': response.get('sales', {}).get('ppsf'),
                'sale_to_list': response.get('sales', {}).get('sale_to_list_ratio')
            }
        }
