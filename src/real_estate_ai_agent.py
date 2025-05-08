"""Real Estate AI Agent
Handles property analysis and query processing with advanced analytics
"""
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv
import asyncio

from .data import DataManager, DataPrioritizer
from .attom_data_fetcher import AttomDataFetcher
from .analysis.hyperlocal_analyzer import HyperlocalAnalyzer
from .analysis.predictive_analyzer import PredictiveAnalyzer

# Load environment variables
load_dotenv()

class RealEstateAIAgent:
    """AI Agent for advanced real estate analysis"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        api_key = os.getenv("ATTOM_API_KEY")
        if not api_key:
            raise ValueError("ATTOM_API_KEY environment variable not set")
            
        self.attom_fetcher = AttomDataFetcher(api_key)
        self.data_manager = DataManager()
        self.data_prioritizer = DataPrioritizer()
        self.hyperlocal_analyzer = HyperlocalAnalyzer()
        self.predictive_analyzer = PredictiveAnalyzer()
        
    async def analyze_property(self, address: str, zipcode: str) -> Dict:
        """Analyze a property using comprehensive data analysis"""
        try:
            # Check cache first
            cached_data = await self.data_manager.get_cached_property_data(address, zipcode)
            if cached_data:
                return cached_data
            
            # Fetch property data
            property_data = await self.attom_fetcher.get_property_details(address, zipcode)
            if not property_data:
                return {"error": "Unable to fetch property data"}
            
            # Get coordinates for hyperlocal analysis
            lat = property_data.get('location', {}).get('latitude')
            lon = property_data.get('location', {}).get('longitude')
            
            # Parallel fetch all required data
            results = await asyncio.gather(
                self.attom_fetcher.get_tax_assessment(address, zipcode),
                self.attom_fetcher.get_owner_info(address, zipcode),
                self.attom_fetcher.get_market_data(zipcode),
                self.hyperlocal_analyzer.get_neighborhood_score(zipcode, lat, lon),
                self.predictive_analyzer.predict_market_trends(zipcode)
            )
            
            tax_data, owner_data, market_data, neighborhood_data, predictions = results
            
            # Combine all data
            analysis = {
                "property": property_data,
                "tax": tax_data,
                "owner": owner_data,
                "market": market_data,
                "neighborhood": neighborhood_data,
                "predictions": predictions,
                "score": self.data_prioritizer.score_property(
                    property_data,
                    tax_data,
                    owner_data,
                    market_data,
                    neighborhood_data
                ),
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the results
            await self.data_manager.cache_property_data(address, zipcode, analysis)
            
            return analysis
            
        except Exception as e:
            self.logger.error(f"Error analyzing property: {str(e)}")
            return {"error": str(e)}
    
    async def search_properties(self, city: str, state: str, zipcode: str) -> List[Dict]:
        """Search for properties with advanced filtering and scoring"""
        try:
            # Check cache first
            cached_results = await self.data_manager.get_cached_search_results(city, state, zipcode)
            if cached_results:
                return cached_results
            
            # Get market predictions first
            predictions = await self.predictive_analyzer.predict_market_trends(zipcode)
            
            # Fetch properties
            properties = await self.attom_fetcher.search_properties(city, state, zipcode)
            if not properties:
                return []
            
            # Score and sort properties
            scored_properties = []
            for prop in properties:
                # Get hyperlocal data for scoring
                lat = prop.get('location', {}).get('latitude')
                lon = prop.get('location', {}).get('longitude')
                neighborhood_data = await self.hyperlocal_analyzer.get_neighborhood_score(
                    zipcode, lat, lon
                )
                
                # Calculate comprehensive score
                score = self.data_prioritizer.comprehensive_score_property(
                    prop,
                    neighborhood_data,
                    predictions
                )
                
                scored_properties.append({
                    **prop,
                    "score": score,
                    "neighborhood": neighborhood_data,
                    "market_prediction": predictions
                })
            
            # Sort by score descending
            scored_properties.sort(key=lambda x: x["score"], reverse=True)
            
            # Cache results
            await self.data_manager.cache_search_results(
                city, state, zipcode, scored_properties
            )
            
            return scored_properties
            
        except Exception as e:
            self.logger.error(f"Error searching properties: {str(e)}")
            return []
    
    async def get_market_insights(self, zipcode: str) -> Dict:
        """Get comprehensive market insights including predictions"""
        try:
            # Check cache first
            cached_data = await self.data_manager.get_cached_market_data(zipcode)
            if cached_data:
                return cached_data
            
            # Fetch all market data in parallel
            results = await asyncio.gather(
                self.attom_fetcher.get_market_data(zipcode),
                self.predictive_analyzer.predict_market_trends(zipcode),
                self.hyperlocal_analyzer.get_neighborhood_score(
                    zipcode,
                    None,  # Use zipcode centroid
                    None
                )
            )
            
            market_data, predictions, neighborhood_data = results
            
            if not market_data:
                return {"error": "Unable to fetch market data"}
            
            # Combine all insights
            insights = {
                "current_market": market_data,
                "predictions": predictions,
                "neighborhood": neighborhood_data,
                "summary": self._generate_market_summary(
                    market_data,
                    predictions,
                    neighborhood_data
                ),
                "timestamp": datetime.now().isoformat()
            }
            
            # Cache the results
            await self.data_manager.cache_market_data(zipcode, insights)
            
            return insights
            
        except Exception as e:
            self.logger.error(f"Error getting market insights: {str(e)}")
            return {"error": str(e)}
    
    def _generate_market_summary(
        self,
        market_data: Dict,
        predictions: Dict,
        neighborhood_data: Dict
    ) -> Dict:
        """Generate a natural language summary of market insights"""
        try:
            summary = {
                "market_strength": self._assess_market_strength(market_data),
                "growth_potential": self._assess_growth_potential(predictions),
                "neighborhood_quality": self._assess_neighborhood(neighborhood_data),
                "investment_recommendation": self._generate_recommendation(
                    market_data,
                    predictions,
                    neighborhood_data
                )
            }
            return summary
        except Exception as e:
            self.logger.error(f"Error generating market summary: {str(e)}")
            return {}
    
    def _assess_market_strength(self, market_data: Dict) -> str:
        """Assess current market strength"""
        # TODO: Implement market strength assessment
        return "Moderate"
    
    def _assess_growth_potential(self, predictions: Dict) -> str:
        """Assess growth potential based on predictions"""
        # TODO: Implement growth potential assessment
        return "High"
    
    def _assess_neighborhood(self, neighborhood_data: Dict) -> str:
        """Assess neighborhood quality"""
        # TODO: Implement neighborhood assessment
        return "Good"
    
    def _generate_recommendation(
        self,
        market_data: Dict,
        predictions: Dict,
        neighborhood_data: Dict
    ) -> str:
        """Generate investment recommendation"""
        # TODO: Implement recommendation logic
        return "Consider investing"
    
    def get_metrics(self) -> Dict:
        """Get usage metrics"""
        return self.data_manager.get_metrics()