"""Realtor.com Scraper Module

This module provides a scraper for Realtor.com real estate data.
"""

import re
import json
import time
from typing import Dict, Any, List, Optional
from urllib.parse import urlencode

from bs4 import BeautifulSoup
import requests

from data_scraping_service.scrapers.base_scraper import BaseScraper

class RealtorScraper(BaseScraper):
    """Scraper for Realtor.com real estate data."""
    
    def __init__(self):
        """Initialize the Realtor.com scraper."""
        super().__init__("Realtor", "https://www.realtor.com", delay_range=(2, 5))
        
        # Additional headers for Realtor.com
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Referer": "https://www.realtor.com/",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
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
                - property_type: Type of property (single-family, condo, etc.)
                - max_results: Maximum number of results to return
            
        Returns:
            List of property data dictionaries
        """
        self.logger.info(f"Searching for properties in {location}")
        
        # Format the location for the URL
        formatted_location = location.replace(" ", "_").replace(",", "_")
        
        # Build the search URL
        search_url = f"{self.base_url}/realestateandhomes-search/{formatted_location}/"
        
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
        
        if "property_type" in kwargs:
            filters["prop_type"] = kwargs["property_type"]
        
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
            # Realtor.com loads property data via JavaScript, so we need to extract it from the page source
            # Look for the data in the script tags
            script_tags = soup.find_all("script", {"type": "text/javascript"})
            
            for script in script_tags:
                if script.string and "window.__PRELOADED_STATE__" in script.string:
                    # Found the data script
                    # Extract the JSON data from the script
                    json_str = re.search(r'window\.__PRELOADED_STATE__ = (.*?);<\/script>', script.string, re.DOTALL)
                    
                    if json_str:
                        data = json.loads(json_str.group(1))
                        
                        if "searchResults" in data and "properties" in data["searchResults"]:
                            results = data["searchResults"]["properties"]
                            
                            for result in results[:max_results]:
                                property_data = {
                                    "id": result.get("property_id", ""),
                                    "address": result.get("address", {}).get("line", ""),
                                    "city": result.get("address", {}).get("city", ""),
                                    "state": result.get("address", {}).get("state_code", ""),
                                    "zip_code": result.get("address", {}).get("postal_code", ""),
                                    "price": result.get("list_price", ""),
                                    "bedrooms": result.get("description", {}).get("beds", ""),
                                    "bathrooms": result.get("description", {}).get("baths", ""),
                                    "square_footage": result.get("description", {}).get("sqft", ""),
                                    "lot_size": result.get("description", {}).get("lot_sqft", ""),
                                    "year_built": result.get("description", {}).get("year_built", ""),
                                    "property_type": result.get("description", {}).get("type", ""),
                                    "url": f"{self.base_url}{result.get('permalink', '')}",
                                    "image_url": result.get("primary_photo", {}).get("href", ""),
                                    "latitude": result.get("location", {}).get("latitude", ""),
                                    "longitude": result.get("location", {}).get("longitude", ""),
                                    "days_on_market": result.get("description", {}).get("days_on_market", ""),
                                    "source": "Realtor.com"
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
            property_id: Realtor.com Property ID
            
        Returns:
            Property details dictionary or None if not found
        """
        self.logger.info(f"Getting details for property {property_id}")
        
        # We need the property URL to get details, but we can't construct it from just the ID
        # This is a limitation of the current implementation
        self.logger.warning("Getting property details by ID is not supported for Realtor.com")
        self.logger.warning("Use the property URL instead")
        
        return None
    
    def get_property_details_by_url(self, property_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific property by URL.
        
        Args:
            property_url: Realtor.com property URL
            
        Returns:
            Property details dictionary or None if not found
        """
        self.logger.info(f"Getting details for property at {property_url}")
        
        # Get the property details page
        soup = self._get_soup(property_url)
        
        if soup is None:
            self.logger.error(f"Failed to get property details page for {property_url}")
            return None
        
        # Extract property details from the page
        property_details = {
            "url": property_url,
            "source": "Realtor.com"
        }
        
        try:
            # Realtor.com loads property data via JavaScript, so we need to extract it from the page source
            # Look for the data in the script tags
            script_tags = soup.find_all("script", {"type": "text/javascript"})
            
            for script in script_tags:
                if script.string and "window.__PRELOADED_STATE__" in script.string:
                    # Found the data script
                    # Extract the JSON data from the script
                    json_str = re.search(r'window\.__PRELOADED_STATE__ = (.*?);<\/script>', script.string, re.DOTALL)
                    
                    if json_str:
                        data = json.loads(json_str.group(1))
                        
                        if "propertyDetails" in data and "data" in data["propertyDetails"]:
                            property_data = data["propertyDetails"]["data"]
                            
                            # Extract property ID
                            property_details["id"] = property_data.get("property_id", "")
                            
                            # Extract basic property information
                            if "location" in property_data:
                                location = property_data["location"]
                                property_details.update({
                                    "address": location.get("address", {}).get("line", ""),
                                    "city": location.get("address", {}).get("city", ""),
                                    "state": location.get("address", {}).get("state_code", ""),
                                    "zip_code": location.get("address", {}).get("postal_code", ""),
                                    "latitude": location.get("latitude", ""),
                                    "longitude": location.get("longitude", "")
                                })
                            
                            # Extract price and other basic details
                            if "description" in property_data:
                                description = property_data["description"]
                                property_details.update({
                                    "price": description.get("list_price", ""),
                                    "bedrooms": description.get("beds", ""),
                                    "bathrooms": description.get("baths", ""),
                                    "square_footage": description.get("sqft", ""),
                                    "lot_size": description.get("lot_sqft", ""),
                                    "year_built": description.get("year_built", ""),
                                    "property_type": description.get("type", ""),
                                    "days_on_market": description.get("days_on_market", "")
                                })
                            
                            # Extract additional property features
                            if "details" in property_data and "features" in property_data["details"]:
                                features = property_data["details"]["features"]
                                
                                # Extract interior features
                                if "interior" in features:
                                    interior = features["interior"]
                                    property_details.update({
                                        "heating": interior.get("heating", ""),
                                        "cooling": interior.get("cooling", ""),
                                        "flooring": interior.get("flooring", "")
                                    })
                                
                                # Extract exterior features
                                if "exterior" in features:
                                    exterior = features["exterior"]
                                    property_details.update({
                                        "parking": exterior.get("parking", ""),
                                        "lot_features": exterior.get("lot_features", "")
                                    })
                            
                            # Extract tax information
                            if "tax_history" in property_data:
                                tax_history = property_data["tax_history"]
                                if tax_history and len(tax_history) > 0:
                                    latest_tax = tax_history[0]
                                    property_details.update({
                                        "property_taxes": latest_tax.get("tax", ""),
                                        "tax_year": latest_tax.get("year", "")
                                    })
                            
                            # Extract price history
                            if "price_history" in property_data:
                                price_history = property_data["price_history"]
                                if price_history and len(price_history) > 0:
                                    price_changes = []
                                    for price_change in price_history:
                                        price_changes.append({
                                            "date": price_change.get("date", ""),
                                            "price": price_change.get("price", ""),
                                            "event": price_change.get("event_name", "")
                                        })
                                    property_details["price_history"] = price_changes
                            
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
        
        # Format the location for the URL
        formatted_location = location.replace(" ", "_").replace(",", "_")
        
        # Build the market data URL
        market_url = f"{self.base_url}/local/{formatted_location}/"
        
        # Get the market data page
        soup = self._get_soup(market_url)
        
        if soup is None:
            self.logger.error(f"Failed to get market data page for {location}")
            return None
        
        # Extract market data from the page
        market_data = {
            "location": location,
            "source": "Realtor.com"
        }
        
        try:
            # Realtor.com loads market data via JavaScript, so we need to extract it from the page source
            # Look for the data in the script tags
            script_tags = soup.find_all("script", {"type": "text/javascript"})
            
            for script in script_tags:
                if script.string and "window.__PRELOADED_STATE__" in script.string:
                    # Found the data script
                    # Extract the JSON data from the script
                    json_str = re.search(r'window\.__PRELOADED_STATE__ = (.*?);<\/script>', script.string, re.DOTALL)
                    
                    if json_str:
                        data = json.loads(json_str.group(1))
                        
                        if "localData" in data and "localRealEstate" in data["localData"]:
                            local_data = data["localData"]["localRealEstate"]
                            
                            # Extract market information
                            market_data.update({
                                "median_listing_price": local_data.get("median_listing_price", ""),
                                "median_sold_price": local_data.get("median_sold_price", ""),
                                "median_days_on_market": local_data.get("median_days_on_market", ""),
                                "median_price_per_sqft": local_data.get("median_price_per_sqft", ""),
                                "active_listings_count": local_data.get("active_listings_count", ""),
                                "price_reduced_count": local_data.get("price_reduced_count", ""),
                                "price_increased_count": local_data.get("price_increased_count", ""),
                                "new_listings_count": local_data.get("new_listings_count", ""),
                                "median_rent_price": local_data.get("median_rent_price", "")
                            })
                            
                            # Extract market trends
                            if "trends" in local_data:
                                trends = local_data["trends"]
                                market_data.update({
                                    "median_listing_price_trend": trends.get("median_listing_price_trend", ""),
                                    "median_days_on_market_trend": trends.get("median_days_on_market_trend", ""),
                                    "active_listings_count_trend": trends.get("active_listings_count_trend", ""),
                                    "new_listings_count_trend": trends.get("new_listings_count_trend", "")
                                })
                            
                            break
                    
                    break
        
        except Exception as e:
            self.logger.error(f"Error extracting market data: {str(e)}")
        
        return market_data
