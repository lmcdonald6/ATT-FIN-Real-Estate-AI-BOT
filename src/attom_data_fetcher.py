"""
ATTOM Data API Client
Handles async HTTP requests to ATTOM API endpoints
"""
import aiohttp
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class AttomDataFetcher:
    """Async client for ATTOM Data API"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "https://api.gateway.attomdata.com"
        self.headers = {
            "apikey": self.api_key,
            "accept": "application/json"
        }
    
    async def fetch_property_data(self, address: str, zipcode: str) -> Dict:
        """Fetch property details from ATTOM API"""
        endpoint = f"{self.base_url}/propertyapi/v1.0.0/property/detail"
        params = {
            "address1": address,
            "postalcode": zipcode
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"ATTOM API error: {response.status} - {await response.text()}")
                        return {}
                        
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching data from ATTOM: {str(e)}")
            return {}
    
    async def search_properties(self, city: str, state: str, zipcode: str) -> Dict:
        """Search for properties in a given area"""
        endpoint = f"{self.base_url}/propertyapi/v1.0.0/property/address"
        params = {
            "city": city,
            "state": state,
            "postalcode": zipcode,
            "page": 1,
            "pagesize": 25
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"ATTOM API error: {response.status} - {await response.text()}")
                        return {}
                        
        except aiohttp.ClientError as e:
            logger.error(f"Error searching properties: {str(e)}")
            return {}
    
    async def get_market_data(self, zipcode: str) -> Dict:
        """Get market statistics for a ZIP code"""
        endpoint = f"{self.base_url}/propertyapi/v1.0.0/property/snapshot"
        params = {
            "postalcode": zipcode,
            "interval": "monthly"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, headers=self.headers, params=params) as response:
                    if response.status == 200:
                        return await response.json()
                    else:
                        logger.error(f"ATTOM API error: {response.status} - {await response.text()}")
                        return {}
                        
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching market data: {str(e)}")
            return {}

# Example usage
if __name__ == "__main__":
    import asyncio
    api_key = "your_attom_api_key"
    fetcher = AttomDataFetcher(api_key)
    loop = asyncio.get_event_loop()
    data = loop.run_until_complete(fetcher.fetch_property_data("123 Main St", "90210"))
    print(data)