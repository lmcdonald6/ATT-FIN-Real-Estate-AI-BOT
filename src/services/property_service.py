from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
import asyncio
from ..data.attom import AttomDataFetcher
from ..analysis.market_analyzer import MarketAnalyzer
from ..analysis.lead_scorer import LeadScorer
from ..utils.cache import Cache

class PropertyService:
    def __init__(self):
        self.attom_fetcher = AttomDataFetcher()
        self.market_analyzer = MarketAnalyzer()
        self.lead_scorer = LeadScorer()
        self.cache = Cache()

    async def search_properties(self, criteria: Dict) -> List[Dict]:
        """Search for properties based on given criteria"""
        cache_key = f"search_{hash(str(criteria))}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result

        try:
            # Get properties from ATTOM API
            properties = await self.attom_fetcher.search_properties(
                location=criteria.get('location'),
                price_min=criteria.get('price_min'),
                price_max=criteria.get('price_max'),
                property_type=criteria.get('property_type')
            )

            # Enrich with market data
            enriched_properties = []
            for prop in properties:
                market_data = await self.market_analyzer.analyze_property(prop['property_id'])
                lead_score = await self.lead_scorer.score_property(prop['property_id'])
                
                enriched_prop = {
                    **prop,
                    'market_data': market_data,
                    'lead_score': lead_score
                }
                enriched_properties.append(enriched_prop)

            self.cache.set(cache_key, enriched_properties, expire=3600)  # Cache for 1 hour
            return enriched_properties

        except Exception as e:
            print(f"Error in property search: {str(e)}")
            return []

    async def get_market_trends(self, zip_code: str) -> Dict:
        """Get market trends for a specific area"""
        cache_key = f"trends_{zip_code}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result

        try:
            trends = await self.market_analyzer.get_market_trends(zip_code)
            self.cache.set(cache_key, trends, expire=3600)  # Cache for 1 hour
            return trends
        except Exception as e:
            print(f"Error getting market trends: {str(e)}")
            return {}

    async def analyze_property(self, property_id: str) -> Dict:
        """Perform detailed analysis of a specific property"""
        cache_key = f"analysis_{property_id}"
        cached_result = self.cache.get(cache_key)
        if cached_result:
            return cached_result

        try:
            # Get property details
            property_details = await self.attom_fetcher.get_property_details(property_id)
            
            # Get market analysis
            market_analysis = await self.market_analyzer.analyze_property(property_id)
            
            # Get lead score
            lead_score = await self.lead_scorer.score_property(property_id)
            
            # Calculate potential ROI
            roi_analysis = await self.calculate_roi(property_details)
            
            analysis = {
                'property_details': property_details,
                'market_analysis': market_analysis,
                'lead_score': lead_score,
                'roi_analysis': roi_analysis,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.cache.set(cache_key, analysis, expire=3600)  # Cache for 1 hour
            return analysis
            
        except Exception as e:
            print(f"Error analyzing property: {str(e)}")
            return {}

    async def calculate_roi(self, property_details: Dict) -> Dict:
        """Calculate potential ROI for a property"""
        try:
            purchase_price = property_details.get('price', 0)
            
            # Estimate repair costs (simplified)
            repair_cost = purchase_price * 0.1  # Assume 10% of purchase price
            
            # Estimate ARV (After Repair Value)
            arv = await self.market_analyzer.estimate_arv(
                property_details['property_id'],
                property_details.get('zip_code')
            )
            
            # Calculate potential profit
            selling_costs = arv * 0.08  # Assume 8% for realtor fees, closing costs, etc.
            holding_costs = purchase_price * 0.02  # Assume 2% for insurance, taxes, utilities
            
            total_costs = purchase_price + repair_cost + selling_costs + holding_costs
            potential_profit = arv - total_costs
            roi_percentage = (potential_profit / total_costs) * 100
            
            return {
                'purchase_price': purchase_price,
                'repair_cost': repair_cost,
                'arv': arv,
                'selling_costs': selling_costs,
                'holding_costs': holding_costs,
                'total_costs': total_costs,
                'potential_profit': potential_profit,
                'roi_percentage': roi_percentage
            }
            
        except Exception as e:
            print(f"Error calculating ROI: {str(e)}")
            return {}
