"""Real Estate AI Agent
Handles property analysis and query processing
"""
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

from .data import DataManager, DataPrioritizer
from .attom_data_fetcher import AttomDataFetcher

# Load environment variables
load_dotenv()

class RealEstateAIAgent:
    """AI Agent for real estate analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        api_key = os.getenv("ATTOM_API_KEY")
        if not api_key:
            raise ValueError("ATTOM_API_KEY environment variable not set")
            
        self.attom_fetcher = AttomDataFetcher(api_key)
        self.data_manager = DataManager()
        self.data_prioritizer = DataPrioritizer()
        
    async def analyze_property(self, address: str, zipcode: str) -> Dict:
        """Analyze a property using ATTOM data"""
        try:
            # Check cache first
            cached_data = await self.data_manager.get_cached_property_data(address, zipcode)
            if cached_data:
                return cached_data
            
            # Fetch fresh data from ATTOM
            property_data = await self.attom_fetcher.get_property_details(address, zipcode)
            if not property_data:
                return {"error": "Unable to fetch property data"}
            
            # Get additional data
            tax_data = await self.attom_fetcher.get_tax_assessment(address, zipcode)
            owner_data = await self.attom_fetcher.get_owner_info(address, zipcode)
            market_data = await self.attom_fetcher.get_market_data(zipcode)
            
            # Combine all data
            analysis = {
                "property": property_data,
                "tax": tax_data,
                "owner": owner_data,
                "market": market_data,
                "score": self.data_prioritizer.score_property(property_data, tax_data, owner_data, market_data),
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the results
            await self.data_manager.cache_property_data(address, zipcode, analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing property: {str(e)}")
            return {"error": str(e)}
    
    async def search_properties(self, city: str, state: str, zipcode: str) -> List[Dict]:
        """Search for properties in a given area"""
        try:
            # Check cache first
            cached_results = await self.data_manager.get_cached_search_results(city, state, zipcode)
            if cached_results:
                return cached_results
            
            # Fetch fresh results
            properties = await self.attom_fetcher.search_properties(city, state, zipcode)
            if not properties:
                return []
            
            # Score and sort properties
            scored_properties = []
            for prop in properties:
                score = self.data_prioritizer.quick_score_property(prop)
                scored_properties.append({
                    **prop,
                    "score": score
                })
            
            # Sort by score descending
            scored_properties.sort(key=lambda x: x["score"], reverse=True)
            
            # Cache results
            await self.data_manager.cache_search_results(city, state, zipcode, scored_properties)
            
            return scored_properties
            
        except Exception as e:
            self.logger.error(f"Error searching properties: {str(e)}")
            return []
    
    async def get_market_insights(self, zipcode: str) -> Dict:
        """Get market insights for a zipcode"""
        try:
            # Check cache first
            cached_data = await self.data_manager.get_cached_market_data(zipcode)
            if cached_data:
                return cached_data
            
            # Fetch fresh market data
            market_data = await self.attom_fetcher.get_market_data(zipcode)
            if not market_data:
                return {"error": "Unable to fetch market data"}
            
            # Cache the results
            await self.data_manager.cache_market_data(zipcode, market_data)
            
            return market_data
            
        except Exception as e:
            self.logger.error(f"Error getting market insights: {str(e)}")
            return {"error": str(e)}
    
    def get_metrics(self) -> Dict:
        """Get usage metrics"""
        return self.data_manager.get_metrics()