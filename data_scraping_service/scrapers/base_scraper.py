"""Base Scraper Module

This module provides a base class for real estate data scrapers.
"""

import os
import json
import time
import random
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
from abc import ABC, abstractmethod

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseScraper(ABC):
    """Base class for real estate data scrapers."""
    
    def __init__(self, name: str, base_url: str, delay_range: tuple = (1, 3)):
        """Initialize the base scraper.
        
        Args:
            name: Name of the scraper
            base_url: Base URL for the website to scrape
            delay_range: Tuple of (min_delay, max_delay) in seconds between requests
        """
        self.name = name
        self.base_url = base_url
        self.delay_range = delay_range
        self.logger = logging.getLogger(f"scraper.{name}")
        self.user_agent = UserAgent()
        self.session = requests.Session()
        
        # Configure session
        self.session.headers.update({
            "User-Agent": self.user_agent.random,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        })
        
        self.logger.info(f"Initialized {name} scraper for {base_url}")
    
    def _get_random_delay(self) -> float:
        """Get a random delay within the configured range.
        
        Returns:
            Random delay in seconds
        """
        return random.uniform(self.delay_range[0], self.delay_range[1])
    
    def _request(self, url: str, method: str = "get", params: Optional[Dict[str, Any]] = None, 
               data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None,
               max_retries: int = 3, retry_delay: int = 5) -> Optional[requests.Response]:
        """Make an HTTP request with retry logic and random delays.
        
        Args:
            url: URL to request
            method: HTTP method (get, post, etc.)
            params: Query parameters
            data: Request data (for POST requests)
            headers: Additional headers
            max_retries: Maximum number of retries
            retry_delay: Delay between retries in seconds
            
        Returns:
            Response object or None if all retries failed
        """
        # Add random delay before request
        time.sleep(self._get_random_delay())
        
        # Update headers with a new random user agent
        request_headers = {"User-Agent": self.user_agent.random}
        if headers:
            request_headers.update(headers)
        
        # Make the request with retry logic
        for attempt in range(max_retries):
            try:
                if method.lower() == "get":
                    response = self.session.get(url, params=params, headers=request_headers)
                elif method.lower() == "post":
                    response = self.session.post(url, params=params, data=data, headers=request_headers)
                else:
                    self.logger.error(f"Unsupported HTTP method: {method}")
                    return None
                
                # Check if the request was successful
                response.raise_for_status()
                return response
            
            except requests.exceptions.RequestException as e:
                self.logger.warning(f"Request failed (attempt {attempt+1}/{max_retries}): {str(e)}")
                
                if attempt < max_retries - 1:
                    # Add a delay before retrying
                    time.sleep(retry_delay)
                    # Increase the delay for the next retry
                    retry_delay *= 2
                else:
                    self.logger.error(f"All retries failed for URL: {url}")
        
        return None
    
    def _get_soup(self, url: str, params: Optional[Dict[str, Any]] = None) -> Optional[BeautifulSoup]:
        """Get a BeautifulSoup object for the given URL.
        
        Args:
            url: URL to request
            params: Query parameters
            
        Returns:
            BeautifulSoup object or None if the request failed
        """
        response = self._request(url, params=params)
        
        if response is None:
            return None
        
        return BeautifulSoup(response.text, "html.parser")
    
    def _save_to_json(self, data: Union[Dict[str, Any], List[Dict[str, Any]]], filename: str) -> bool:
        """Save data to a JSON file.
        
        Args:
            data: Data to save
            filename: Name of the file to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create the output directory if it doesn't exist
            os.makedirs("data", exist_ok=True)
            
            # Add a timestamp to the filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"data/{filename}_{timestamp}.json"
            
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            
            self.logger.info(f"Saved data to {filename}")
            return True
        
        except Exception as e:
            self.logger.error(f"Error saving data to {filename}: {str(e)}")
            return False
    
    @abstractmethod
    def search_properties(self, location: str, **kwargs) -> List[Dict[str, Any]]:
        """Search for properties in the given location.
        
        Args:
            location: Location to search in (city, zip code, etc.)
            **kwargs: Additional search parameters
            
        Returns:
            List of property data dictionaries
        """
        pass
    
    @abstractmethod
    def get_property_details(self, property_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed information for a specific property.
        
        Args:
            property_id: ID of the property to get details for
            
        Returns:
            Property details dictionary or None if not found
        """
        pass
    
    @abstractmethod
    def get_market_data(self, location: str) -> Optional[Dict[str, Any]]:
        """Get market data for the given location.
        
        Args:
            location: Location to get market data for (city, zip code, etc.)
            
        Returns:
            Market data dictionary or None if not found
        """
        pass
