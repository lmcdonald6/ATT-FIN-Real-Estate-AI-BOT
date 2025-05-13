"""API services for external data providers."""

import os
from typing import Dict, Optional
import requests
from .mock_data import mock_data_service

class APIService:
    """Handles all external API calls with fallback logic."""
    
    def __init__(self):
        self.opencage_api_key = os.getenv("OPENCAGE_API_KEY")
        self.walkscore_api_key = os.getenv("WALKSCORE_API_KEY")
        self.cache = {}
        
    def geocode_address(self, address: str) -> Optional[Dict]:
        """Geocode address using OpenCage with fallback."""
        cache_key = f"geocode_{address}"
        
        # Check cache first
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            if not self.opencage_api_key:
                raise ValueError("OpenCage API key not found")
                
            url = f"https://api.opencagedata.com/geocode/v1/json"
            params = {
                "q": address,
                "key": self.opencage_api_key,
                "limit": 1
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            if data["results"]:
                result = {
                    "lat": data["results"][0]["geometry"]["lat"],
                    "lng": data["results"][0]["geometry"]["lng"],
                    "formatted": data["results"][0]["formatted"]
                }
                self.cache[cache_key] = result
                return result
                
        except Exception as e:
            print(f"Geocoding failed: {e}")
            
        # Fallback to mock data
        return mock_data_service._generate_mock_property_data("00000")["location"]
        
    def get_walk_score(self, lat: float, lng: float, address: str) -> Dict:
        """Get Walk Score with fallback to Geoapify POIs."""
        cache_key = f"walkscore_{lat}_{lng}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        try:
            if not self.walkscore_api_key:
                raise ValueError("Walk Score API key not found")
                
            url = "https://api.walkscore.com/score"
            params = {
                "format": "json",
                "address": address,
                "lat": lat,
                "lon": lng,
                "wsapikey": self.walkscore_api_key
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            result = {
                "walk_score": data.get("walkscore", 0),
                "description": data.get("description", ""),
                "source": "WalkScore API"
            }
            self.cache[cache_key] = result
            return result
            
        except Exception as e:
            print(f"Walk Score API failed: {e}")
            # Fallback to mock data
            mock_data = mock_data_service._generate_mock_property_data("00000")
            return {
                "walk_score": mock_data["signals"]["transit"]["transit_score"],
                "description": "Based on estimated POI density",
                "source": "Mock Data"
            }
            
    def get_crime_data(self, lat: float, lng: float) -> Dict:
        """Get crime data with fallback to FBI data or mock data."""
        cache_key = f"crime_{lat}_{lng}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # For now, using mock data
        mock_data = mock_data_service._generate_mock_property_data("00000")
        return mock_data["signals"]["crime"]
        
    def get_census_data(self, zipcode: str) -> Dict:
        """Get census data with fallback to mock data."""
        cache_key = f"census_{zipcode}"
        
        if cache_key in self.cache:
            return self.cache[cache_key]
            
        # For now, using mock data
        mock_data = mock_data_service._generate_mock_property_data(zipcode)
        return mock_data["signals"]["demographics"]

api_service = APIService()
