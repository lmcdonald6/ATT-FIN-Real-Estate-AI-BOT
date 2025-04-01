"""
Enhanced ATTOM API client with in-memory caching
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import aiohttp
import json
import os
from dotenv import load_dotenv

from .data import DataManager
from .attom_data_fetcher import AttomDataFetcher

# Load environment variables
load_dotenv()

class RealEstateDataAPI:
    """Enhanced ATTOM API client with caching"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv('ATTOM_API_KEY')
        if not self.api_key:
            raise ValueError("ATTOM_API_KEY environment variable not set")
            
        self.base_url = "https://api.attomdata.com/v2"
        self.data_manager = DataManager()
    
    async def get_property_details(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get property details with caching"""
        try:
            # Check cache first
            cached = await self.data_manager.get_cached_property_data(address, zipcode)
            if cached:
                return cached
            
            # Make API request
            endpoint = f"{self.base_url}/property/detail"
            params = {
                'address': address,
                'zipcode': zipcode
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, headers={'apikey': self.api_key}) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Cache the results
                        await self.data_manager.cache_property_data(address, zipcode, data)
                        return data
                    else:
                        self.logger.error(f"ATTOM API error: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error getting property details: {str(e)}")
            return None
    
    async def search_properties(self, city: str, state: str, zipcode: str) -> List[Dict]:
        """Search for properties in an area"""
        try:
            # Check cache first
            cached = await self.data_manager.get_cached_search_results(city, state, zipcode)
            if cached:
                return cached
            
            # Make API request
            endpoint = f"{self.base_url}/property/search"
            params = {
                'city': city,
                'state': state,
                'zipcode': zipcode,
                'status': 'ForSale'
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, headers={'apikey': self.api_key}) as response:
                    if response.status == 200:
                        data = await response.json()
                        properties = data.get('properties', [])
                        # Cache the results
                        await self.data_manager.cache_search_results(city, state, zipcode, properties)
                        return properties
                    else:
                        self.logger.error(f"ATTOM API error: {response.status}")
                        return []
                        
        except Exception as e:
            self.logger.error(f"Error searching properties: {str(e)}")
            return []
    
    async def get_market_data(self, zipcode: str) -> Optional[Dict]:
        """Get market data for a zipcode"""
        try:
            # Check cache first
            cached = await self.data_manager.get_cached_market_data(zipcode)
            if cached:
                return cached
            
            # Make API request
            endpoint = f"{self.base_url}/market/snapshot"
            params = {'zipcode': zipcode}
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, headers={'apikey': self.api_key}) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Cache the results
                        await self.data_manager.cache_market_data(zipcode, data)
                        return data
                    else:
                        self.logger.error(f"ATTOM API error: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error getting market data: {str(e)}")
            return None
    
    async def get_owner_info(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get owner information"""
        try:
            # Check cache first
            cached = await self.data_manager.get_cached_owner_data(address, zipcode)
            if cached:
                return cached
            
            # Make API request
            endpoint = f"{self.base_url}/property/owner"
            params = {
                'address': address,
                'zipcode': zipcode
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, headers={'apikey': self.api_key}) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Cache the results
                        await self.data_manager.cache_owner_data(address, zipcode, data)
                        return data
                    else:
                        self.logger.error(f"ATTOM API error: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error getting owner info: {str(e)}")
            return None
    
    async def get_tax_assessment(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get tax assessment data"""
        try:
            # Check cache first
            cached = await self.data_manager.get_cached_tax_data(address, zipcode)
            if cached:
                return cached
            
            # Make API request
            endpoint = f"{self.base_url}/property/tax"
            params = {
                'address': address,
                'zipcode': zipcode
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.get(endpoint, params=params, headers={'apikey': self.api_key}) as response:
                    if response.status == 200:
                        data = await response.json()
                        # Cache the results
                        await self.data_manager.cache_tax_data(address, zipcode, data)
                        return data
                    else:
                        self.logger.error(f"ATTOM API error: {response.status}")
                        return None
                        
        except Exception as e:
            self.logger.error(f"Error getting tax assessment: {str(e)}")
            return None
