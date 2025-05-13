"""Zillow Scraper Module

This module provides a scraper for Zillow real estate data.
"""

import re
import json
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

from bs4 import BeautifulSoup
import requests

from data_scraping_service.scrapers.base_scraper import BaseScraper

class ZillowScraper(BaseScraper):
    """Scraper for Zillow real estate data."""
    
    def __init__(self):
        """Initialize the Zillow scraper."""
        super().__init__("Zillow", "https://www.zillow.com", delay_range=(2, 5))
        
        # Additional headers for Zillow
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.zillow.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "same-origin",
            "Sec-Fetch-User": "?1",
            "Cache-Control": "max-age=0"
        })
    
    def search_properties(self, location: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for properties in the given location.
        
        Args:
            location: Location to search in (city, state, zip code, etc.)
            **kwargs: Additional search parameters
                - min_price: Minimum price
                - max_price: Maximum price
                - min_beds: Minimum number of bedrooms
                - min_baths: Minimum number of bathrooms
                - home_type: Type of home (house, apartment, condo, etc.)
                - max_results: Maximum number of results to return
            
        Returns:
            List of property data dictionaries
        """
        self.logger.info(f"Searching for properties in {location}")
        
        # Build the search URL
        search_url = f"{self.base_url}/homes/{location}/"
        
        # Add filters to the URL if provided
        filters = {}
        
        if "min_price" in kwargs:
            filters["price_min"] = kwargs["min_price"]
        
        if "max_price" in kwargs:
            filters["price_max"] = kwargs["max_price"]
        
        if "min_beds" in kwargs:
            filters["beds_min"] = kwargs["min_beds"]
        
        if "min_baths" in kwargs:
            filters["baths_min"] = kwargs["min_baths"]
        
        if "home_type" in kwargs:
            filters["home_type"] = kwargs["home_type"]
        
        if filters:
            search_url += "?" + urlencode(filters)
        
        # Get the search results page
        self.logger.info(f"Requesting search URL: {search_url}")
        soup = self._get_soup(search_url)
        
        if soup is None:
            self.logger.error("Failed to get search results page")
            return []
        
        # Extract property data from the search results
        properties = []
        max_results = kwargs.get("max_results", 20)
        
        try:
            # Zillow loads property data via JavaScript, so we need to extract it from the page source
            # Look for the data in the script tags
            script_tags = soup.find_all("script", {"type": "application/json"})
            
            for script in script_tags:
                if script.string and """"queryState""" in script.string:
                    # Found the data script
                    data = json.loads(script.string)
                    
                    if "cat1" in data and "searchResults" in data["cat1"] and "listResults" in data["cat1"]["searchResults"]:
                        results = data["cat1"]["searchResults"]["listResults"]
                        
                        for result in results[:max_results]:
                            property_data = {
                                "id": result.get("zpid", ""),
                                "address": result.get("address", ""),
                                "price": result.get("price", ""),
                                "bedrooms": result.get("beds", ""),
                                "bathrooms": result.get("baths", ""),
                                "square_footage": result.get("area", ""),
                                "url": f"{self.base_url}/homedetails/{result.get('zpid', '')}_zpid/",
                                "image_url": result.get("imgSrc", ""),
                                "latitude": result.get("latLong", {}).get("latitude", ""),
                                "longitude": result.get("latLong", {}).get("longitude", ""),
                                "property_type": result.get("hdpData", {}).get("homeInfo", {}).get("propertyType", ""),
                                "year_built": result.get("hdpData", {}).get("homeInfo", {}).get("yearBuilt", ""),
                                "days_on_zillow": result.get("hdpData", {}).get("homeInfo", {}).get("daysOnZillow", ""),
                                "source": "Zillow"
                            }
                            
                            properties.append(property_data)
                    
                    break
        
        except Exception as e:
            self.logger.error(f"Error extracting property data: {str(e)}")
        
        self.logger.info(f"Found {len(properties)} properties in {location}")
        return properties
    
    def get_property_details(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific property.
        
        Args:
            property_id: Zillow Property ID (zpid)
            
        Returns:
            Property details dictionary or None if not found
        """
        self.logger.info(f"Getting details for property {property_id}")
        
        # Build the property details URL
        property_url = f"{self.base_url}/homedetails/{property_id}_zpid/"
        
        # Get the property details page
        soup = self._get_soup(property_url)
        
        if soup is None:
            self.logger.error(f"Failed to get property details page for {property_id}")
            return None
        
        # Extract property details from the page
        property_details = {
            "id": property_id,
            "url": property_url,
            "source": "Zillow"
        }
        
        try:
            # Zillow loads property data via JavaScript, so we need to extract it from the page source
            # Look for the data in the script tags
            script_tags = soup.find_all("script", {"type": "application/json"})
            
            for script in script_tags:
                if script.string and """"apiCache""" in script.string:
                    # Found the data script
                    data = json.loads(script.string)
                    
                    # Navigate the complex data structure to find property details
                    for key in data.keys():
                        if "property" in key.lower():
                            property_data = data[key]["property"]
                            
                            # Extract basic property information
                            property_details.update({
                                "address": property_data.get("address", {}).get("streetAddress", ""),
                                "city": property_data.get("address", {}).get("city", ""),
                                "state": property_data.get("address", {}).get("state", ""),
                                "zip_code": property_data.get("address", {}).get("zipcode", ""),
                                "price": property_data.get("price", ""),
                                "bedrooms": property_data.get("bedrooms", ""),
                                "bathrooms": property_data.get("bathrooms", ""),
                                "square_footage": property_data.get("livingArea", ""),
                                "lot_size": property_data.get("lotSize", ""),
                                "year_built": property_data.get("yearBuilt", ""),
                                "property_type": property_data.get("propertyType", ""),
                                "description": property_data.get("description", ""),
                                "days_on_zillow": property_data.get("daysOnZillow", ""),
                                "latitude": property_data.get("latitude", ""),
                                "longitude": property_data.get("longitude", ""),
                                "zestimate": property_data.get("zestimate", ""),
                                "rent_zestimate": property_data.get("rentZestimate", "")
                            })
                            
                            # Extract additional property features
                            if "resoFacts" in property_data:
                                property_details.update({
                                    "heating": property_data["resoFacts"].get("heating", ""),
                                    "cooling": property_data["resoFacts"].get("cooling", ""),
                                    "parking": property_data["resoFacts"].get("parking", ""),
                                    "lot_size_acres": property_data["resoFacts"].get("lotSizeAcres", "")
                                })
                            
                            # Extract tax information
                            if "taxHistory" in property_data:
                                tax_history = property_data["taxHistory"]
                                if tax_history and len(tax_history) > 0:
                                    latest_tax = tax_history[0]
                                    property_details["property_taxes"] = latest_tax.get("taxPaid", "")
                                    property_details["tax_year"] = latest_tax.get("time", "")
                            
                            break
                    
                    break
        
        except Exception as e:
            self.logger.error(f"Error extracting property details: {str(e)}")
        
        return property_details
    
    def get_market_data(self, location: str) -> Optional[Dict[str, Any]]:
        """Get market data for the given location.
        
        Args:
            location: Location to get market data for (city, state, zip code, etc.)
            
        Returns:
            Market data dictionary or None if not found
        """
        self.logger.info(f"Getting market data for {location}")
        
        # Build the market data URL
        market_url = f"{self.base_url}/homes/{location}/home-values/"
        
        # Get the market data page
        soup = self._get_soup(market_url)
        
        if soup is None:
            self.logger.error(f"Failed to get market data page for {location}")
            return None
        
        # Extract market data from the page
        market_data = {
            "location": location,
            "source": "Zillow"
        }
        
        try:
            # Zillow loads market data via JavaScript, so we need to extract it from the page source
            # Look for the data in the script tags
            script_tags = soup.find_all("script", {"type": "application/json"})
            
            for script in script_tags:
                if script.string and """"marketData""" in script.string:
                    # Found the data script
                    data = json.loads(script.string)
                    
                    # Navigate the complex data structure to find market data
                    for key in data.keys():
                        if "market" in key.lower():
                            market_info = data[key]
                            
                            # Extract market information
                            if "regionData" in market_info:
                                region_data = market_info["regionData"]
                                
                                market_data.update({
                                    "median_home_value": region_data.get("median_home_value", ""),
                                    "median_list_price": region_data.get("median_list_price", ""),
                                    "median_sale_price": region_data.get("median_sale_price", ""),
                                    "median_price_per_sqft": region_data.get("median_price_per_sqft", ""),
                                    "median_rent_price": region_data.get("median_rent_price", ""),
                                    "price_to_rent_ratio": region_data.get("price_to_rent_ratio", ""),
                                    "market_temperature": region_data.get("market_temperature", ""),
                                    "median_days_on_market": region_data.get("median_days_on_market", ""),
                                    "median_sale_to_list_ratio": region_data.get("median_sale_to_list_ratio", ""),
                                    "percent_homes_decreasing": region_data.get("percent_homes_decreasing", ""),
                                    "percent_listing_price_cut": region_data.get("percent_listing_price_cut", ""),
                                    "percent_selling_for_gain": region_data.get("percent_selling_for_gain", ""),
                                    "percent_selling_for_loss": region_data.get("percent_selling_for_loss", ""),
                                    "foreclosure_rate": region_data.get("foreclosure_rate", ""),
                                    "median_property_tax": region_data.get("median_property_tax", "")
                                })
                            
                            # Extract market forecast
                            if "marketForecast" in market_info:
                                forecast = market_info["marketForecast"]
                                
                                market_data.update({
                                    "forecast_appreciation_1yr": forecast.get("forecast_appreciation_1yr", ""),
                                    "forecast_median_value_1yr": forecast.get("forecast_median_value_1yr", ""),
                                    "forecast_market_temperature": forecast.get("forecast_market_temperature", "")
                                })
                            
                            break
                    
                    break
        
        except Exception as e:
            self.logger.error(f"Error extracting market data: {str(e)}")
        
        return market_data
