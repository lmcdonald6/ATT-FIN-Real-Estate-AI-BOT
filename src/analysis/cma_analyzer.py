"""Automated Comparative Market Analysis (CMA) system."""
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors
from typing import Dict, List, Optional, Tuple

class CMAAnalyzer:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.feature_weights = {
            'sqft': 0.25,
            'beds': 0.15,
            'baths': 0.15,
            'lot_size': 0.10,
            'age': 0.10,
            'condition': 0.15,
            'location': 0.10
        }
        
    def generate_cma(self,
                    target_property: Dict,
                    comparable_properties: pd.DataFrame,
                    market_data: pd.DataFrame,
                    radius_miles: float = 1.0,
                    max_comps: int = 5) -> Dict:
        """Generate comprehensive CMA report for target property."""
        # Find comparable properties
        comps = self._find_comparables(
            target_property,
            comparable_properties,
            radius_miles,
            max_comps
        )
        
        # Calculate adjusted values
        adjusted_comps = self._adjust_comparable_values(target_property, comps)
        
        # Generate CMA report
        report = {
            'target_property': target_property,
            'comparable_properties': adjusted_comps.to_dict('records'),
            'value_analysis': self._analyze_value(target_property, adjusted_comps),
            'market_conditions': self._analyze_market_conditions(market_data, target_property),
            'price_insights': self._generate_price_insights(target_property, adjusted_comps),
            'recommendations': self._generate_recommendations(target_property, adjusted_comps, market_data)
        }
        
        return report
    
    def _find_comparables(self,
                         target: Dict,
                         properties: pd.DataFrame,
                         radius_miles: float,
                         max_comps: int) -> pd.DataFrame:
        """Find most similar properties within specified radius."""
        # Filter by location radius
        nearby = self._filter_by_distance(
            properties,
            target['latitude'],
            target['longitude'],
            radius_miles
        )
        
        if len(nearby) == 0:
            return pd.DataFrame()
            
        # Prepare features for similarity comparison
        features = self._prepare_comparison_features(nearby, target)
        
        # Find nearest neighbors
        nbrs = NearestNeighbors(n_neighbors=min(max_comps, len(nearby)))
        nbrs.fit(features)
        
        # Get indices of most similar properties
        distances, indices = nbrs.kneighbors(
            self._prepare_comparison_features(pd.DataFrame([target]), target)
        )
        
        # Return comparable properties with similarity scores
        comps = nearby.iloc[indices[0]].copy()
        comps['similarity_score'] = 1 - (distances[0] / distances[0].max())
        
        return comps
    
    def _filter_by_distance(self,
                          properties: pd.DataFrame,
                          lat: float,
                          lon: float,
                          radius_miles: float) -> pd.DataFrame:
        """Filter properties within specified radius."""
        # Calculate distances using Haversine formula
        R = 3959.87433  # Earth's radius in miles
        
        properties['distance'] = np.rad2deg(
            np.arccos(
                np.sin(np.deg2rad(lat)) * np.sin(np.deg2rad(properties['latitude'])) +
                np.cos(np.deg2rad(lat)) * np.cos(np.deg2rad(properties['latitude'])) *
                np.cos(np.deg2rad(properties['longitude'] - lon))
            )
        ) * R
        
        return properties[properties['distance'] <= radius_miles]
    
    def _prepare_comparison_features(self,
                                   properties: pd.DataFrame,
                                   target: Dict) -> np.ndarray:
        """Prepare and normalize features for comparison."""
        features = []
        
        for feature, weight in self.feature_weights.items():
            if feature == 'location':
                # Location similarity based on distance
                if 'distance' in properties.columns:
                    feat = 1 - (properties['distance'] / properties['distance'].max())
                else:
                    feat = np.ones(len(properties))
            else:
                feat = properties[feature]
                
                # Normalize feature
                feat = (feat - feat.min()) / (feat.max() - feat.min() + 1e-10)
                
            features.append(feat * weight)
            
        return np.column_stack(features)
    
    def _adjust_comparable_values(self,
                                target: Dict,
                                comps: pd.DataFrame) -> pd.DataFrame:
        """Adjust comparable property values based on differences."""
        adjusted = comps.copy()
        
        # Standard adjustment factors
        adjustments = {
            'sqft': 100,  # $ per sqft
            'beds': 5000,  # $ per bedroom
            'baths': 7500,  # $ per bathroom
            'lot_size': 2,  # $ per sqft of lot
            'age': -1000,  # $ per year of age
            'condition': 10000  # $ per condition point (1-5)
        }
        
        # Calculate adjustments
        for feature, factor in adjustments.items():
            if feature in target and feature in adjusted.columns:
                diff = target[feature] - adjusted[feature]
                adjusted[f'{feature}_adjustment'] = diff * factor
                
        # Apply total adjustments
        adjustment_cols = [col for col in adjusted.columns if col.endswith('_adjustment')]
        adjusted['total_adjustment'] = adjusted[adjustment_cols].sum(axis=1)
        adjusted['adjusted_price'] = adjusted['price'] + adjusted['total_adjustment']
        
        return adjusted
    
    def _analyze_value(self,
                      target: Dict,
                      comps: pd.DataFrame) -> Dict:
        """Analyze property value based on comparables."""
        adjusted_prices = comps['adjusted_price']
        
        analysis = {
            'suggested_price_range': {
                'low': adjusted_prices.quantile(0.25),
                'median': adjusted_prices.median(),
                'high': adjusted_prices.quantile(0.75)
            },
            'price_metrics': {
                'average': adjusted_prices.mean(),
                'std_dev': adjusted_prices.std(),
                'price_per_sqft': adjusted_prices.mean() / target['sqft']
            },
            'confidence_score': self._calculate_confidence_score(target, comps)
        }
        
        return analysis
    
    def _analyze_market_conditions(self,
                                 market_data: pd.DataFrame,
                                 target: Dict) -> Dict:
        """Analyze current market conditions."""
        recent_data = market_data[
            market_data['period'] >= market_data['period'].max() - pd.DateOffset(months=6)
        ]
        
        return {
            'median_dom': recent_data['days_on_market'].median(),
            'inventory_level': len(recent_data[recent_data['status'] == 'active']),
            'price_trend': self._calculate_price_trend(recent_data),
            'market_type': self._determine_market_type(recent_data),
            'seasonality': self._analyze_seasonality(market_data)
        }
    
    def _calculate_confidence_score(self,
                                  target: Dict,
                                  comps: pd.DataFrame) -> float:
        """Calculate confidence score for the CMA."""
        factors = []
        
        # Number of comps factor
        num_comps = len(comps)
        factors.append(min(num_comps / 5, 1.0))
        
        # Similarity score factor
        factors.append(comps['similarity_score'].mean())
        
        # Adjustment factor (lower adjustments = higher confidence)
        avg_adjustment_pct = abs(comps['total_adjustment'] / comps['price']).mean()
        factors.append(1 - min(avg_adjustment_pct, 1))
        
        # Price consistency factor
        price_cv = comps['adjusted_price'].std() / comps['adjusted_price'].mean()
        factors.append(1 - min(price_cv, 1))
        
        return np.mean(factors) * 100
    
    def _calculate_price_trend(self, market_data: pd.DataFrame) -> float:
        """Calculate recent price trend."""
        monthly_prices = market_data.groupby('period')['price'].median()
        if len(monthly_prices) < 2:
            return 0
            
        return ((monthly_prices.iloc[-1] / monthly_prices.iloc[0]) - 1) * 100
    
    def _determine_market_type(self, market_data: pd.DataFrame) -> str:
        """Determine market type based on conditions."""
        active = len(market_data[market_data['status'] == 'active'])
        sold = len(market_data[market_data['status'] == 'sold'])
        
        if active == 0 or sold == 0:
            return "Insufficient data"
            
        months_inventory = active / (sold / 6)  # 6 months of data
        
        if months_inventory < 3:
            return "Seller's Market"
        elif months_inventory > 6:
            return "Buyer's Market"
        else:
            return "Balanced Market"
    
    def _analyze_seasonality(self, market_data: pd.DataFrame) -> Dict:
        """Analyze seasonal patterns in the market."""
        monthly_sales = market_data[market_data['status'] == 'sold'].groupby(
            market_data['period'].dt.month
        ).size()
        
        peak_month = monthly_sales.idxmax()
        slow_month = monthly_sales.idxmin()
        
        return {
            'peak_month': peak_month,
            'slow_month': slow_month,
            'seasonality_factor': monthly_sales.max() / monthly_sales.min()
        }
    
    def _generate_price_insights(self,
                               target: Dict,
                               comps: pd.DataFrame) -> List[str]:
        """Generate insights about property pricing."""
        insights = []
        
        # Price position insight
        target_price = target.get('list_price', target.get('price', 0))
        median_price = comps['adjusted_price'].median()
        
        price_diff_pct = (target_price - median_price) / median_price * 100
        
        if abs(price_diff_pct) <= 5:
            insights.append("Price is well-aligned with comparable properties")
        elif price_diff_pct > 5:
            insights.append(f"Price is {price_diff_pct:.1f}% above comparable properties")
        else:
            insights.append(f"Price is {-price_diff_pct:.1f}% below comparable properties")
            
        # Value factors
        high_features = []
        low_features = []
        
        for feature in ['sqft', 'beds', 'baths', 'lot_size']:
            if feature in target and feature in comps.columns:
                avg_value = comps[feature].mean()
                if target[feature] > avg_value * 1.1:
                    high_features.append(feature)
                elif target[feature] < avg_value * 0.9:
                    low_features.append(feature)
                    
        if high_features:
            insights.append(f"Property has above-average {', '.join(high_features)}")
        if low_features:
            insights.append(f"Property has below-average {', '.join(low_features)}")
            
        return insights
    
    def _generate_recommendations(self,
                                target: Dict,
                                comps: pd.DataFrame,
                                market_data: pd.DataFrame) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []
        
        # Pricing recommendations
        target_price = target.get('list_price', target.get('price', 0))
        suggested_price = comps['adjusted_price'].median()
        
        if target_price > suggested_price * 1.1:
            recommendations.append("Consider price reduction to align with market values")
        elif target_price < suggested_price * 0.9:
            recommendations.append("Property may be underpriced for its features")
            
        # Market timing
        market_type = self._determine_market_type(market_data)
        if market_type == "Seller's Market":
            recommendations.append("Strong seller's market - consider aggressive pricing")
        elif market_type == "Buyer's Market":
            recommendations.append("Buyer's market - focus on property presentation and competitive pricing")
            
        # Feature highlights
        unique_features = set()
        for feature in ['sqft', 'beds', 'baths', 'lot_size']:
            if feature in target and feature in comps.columns:
                if target[feature] > comps[feature].quantile(0.75):
                    unique_features.add(feature)
                    
        if unique_features:
            recommendations.append(
                f"Highlight superior {', '.join(unique_features)} in marketing"
            )
            
        return recommendations
