"""
AI agent for real estate analysis and recommendations.
Integrates multiple AI providers and advanced property analysis.
"""
from typing import Dict, List, Optional, Any
from .model_provider import ModelProviderFactory, FallbackProvider, ModelResponse
from .property_analyzer import PropertyAnalyzer
import json
import logging

logger = logging.getLogger(__name__)

class RealEstateAgent:
    """Intelligent real estate agent powered by multiple AI providers"""
    
    def __init__(self, provider_name: str = 'fallback'):
        self.provider = ModelProviderFactory.create_provider(provider_name)
        self.analyzer = PropertyAnalyzer()
        
    def analyze_user_intent(self, message: str) -> Dict[str, Any]:
        """Analyze user message to understand their requirements"""
        try:
            # Get intent from AI provider
            response = self.provider.analyze_intent(message)
            if not response.content:
                return {'error': 'Failed to analyze intent'}
                
            # Parse the response
            intent = json.loads(response.content)
            
            # Enhance with additional analysis
            if 'property_preferences' in intent:
                # Clean and normalize preferences
                preferences = intent['property_preferences']
                if 'price_range' in preferences:
                    price_range = preferences['price_range']
                    if isinstance(price_range, str):
                        # Convert price strings like "500k" to numbers
                        price_range = price_range.replace('k', '000')
                        price_range = price_range.replace('m', '000000')
                        preferences['price_range'] = float(price_range)
                        
            return intent
            
        except Exception as e:
            logger.error(f"Error analyzing user intent: {str(e)}")
            return {'error': str(e)}
            
    def search_properties(
        self,
        criteria: Dict[str, Any],
        available_properties: List[Dict]
    ) -> List[Dict]:
        """Search for properties matching user criteria with intelligent ranking"""
        try:
            # Preprocess property data
            df = self.analyzer.preprocess_property_data(available_properties)
            
            # Filter properties based on criteria
            filtered = []
            for prop in available_properties:
                if self._matches_criteria(prop, criteria):
                    # Get property insights
                    insights = self.analyzer.get_property_insights(prop)
                    
                    # Add insights to property data
                    enhanced_prop = {
                        **prop,
                        'analysis': insights
                    }
                    filtered.append(enhanced_prop)
            
            # Sort properties by relevance
            filtered.sort(
                key=lambda p: (
                    p['analysis'].get('investment_potential', 0),
                    p['analysis'].get('location_score', 0)
                ),
                reverse=True
            )
            
            return filtered
            
        except Exception as e:
            logger.error(f"Error searching properties: {str(e)}")
            return []
            
    def generate_property_recommendation(
        self,
        property_data: Dict,
        user_preferences: Dict
    ) -> str:
        """Generate personalized property recommendation"""
        try:
            # Get property insights
            insights = self.analyzer.get_property_insights(property_data)
            
            # Find similar properties
            similar = self.analyzer.find_similar_properties(
                property_data,
                [property_data],  # This should be expanded with more properties
                n_similar=3
            )
            
            # Create context for AI response
            context = {
                'property': property_data,
                'insights': insights,
                'similar_properties': similar,
                'user_preferences': user_preferences
            }
            
            # Generate recommendation using AI provider
            response = self.provider.generate_response(
                "Generate a property recommendation",
                context
            )
            
            return response.content if response.content else "Unable to generate recommendation"
            
        except Exception as e:
            logger.error(f"Error generating recommendation: {str(e)}")
            return str(e)
            
    def _matches_criteria(self, property_data: Dict, criteria: Dict) -> bool:
        """Check if property matches search criteria"""
        try:
            for key, value in criteria.items():
                if key not in property_data:
                    continue
                    
                if key == 'price_range':
                    if isinstance(value, (list, tuple)):
                        min_price, max_price = value
                        if not (min_price <= property_data['price'] <= max_price):
                            return False
                    else:
                        if property_data['price'] > value:
                            return False
                            
                elif key == 'location':
                    if value.lower() not in property_data['location'].lower():
                        return False
                        
                elif key in ['bedrooms', 'bathrooms']:
                    if property_data[key] < value:
                        return False
                        
            return True
            
        except Exception as e:
            logger.error(f"Error matching criteria: {str(e)}")
            return False
            
    def get_market_insights(self, properties: List[Dict]) -> Dict[str, Any]:
        """Generate market insights from property data"""
        try:
            df = self.analyzer.preprocess_property_data(properties)
            
            insights = {
                'price_trends': {
                    'median_price': df['price'].median(),
                    'price_range': [df['price'].min(), df['price'].max()],
                    'price_per_sqft_avg': df['price_per_sqft'].mean()
                },
                'property_types': {
                    'bedrooms': df['bedrooms'].value_counts().to_dict(),
                    'bathrooms': df['bathrooms'].value_counts().to_dict()
                },
                'outliers': {
                    'price': df[df['price_is_outlier']].shape[0],
                    'sqft': df[df['sqft_is_outlier']].shape[0]
                }
            }
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating market insights: {str(e)}")
            return {'error': str(e)}
