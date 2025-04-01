"""
Machine learning models for real estate market analysis.
Focuses on price trends and investment opportunities.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split

class MarketPredictor:
    """
    ML-based market analysis and prediction.
    Uses historical data and market indicators.
    """
    
    def __init__(self):
        # Initialize models
        self.price_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        self.trend_model = RandomForestRegressor(
            n_estimators=100,
            max_depth=8,
            random_state=42
        )
        
        # Data preprocessing
        self.scaler = StandardScaler()
        self.feature_columns = [
            'median_price',
            'price_trend',
            'inventory_trend',
            'median_dom',
            'sf_ratio',      # Single Family ratio
            'condo_ratio',   # Condo ratio
            'avg_year_built',
            'avg_lot_size',
            'seasonal_factor'
        ]
        
        # Market indicators
        self.market_indicators = {
            # Nashville
            "37215": {
                "employment_growth": 0.03,
                "population_growth": 0.02,
                "income_growth": 0.04,
                "development_score": 0.8
            },
            "37203": {
                "employment_growth": 0.04,
                "population_growth": 0.03,
                "income_growth": 0.035,
                "development_score": 0.9
            },
            # Atlanta
            "30305": {
                "employment_growth": 0.035,
                "population_growth": 0.025,
                "income_growth": 0.045,
                "development_score": 0.85
            },
            "30308": {
                "employment_growth": 0.045,
                "population_growth": 0.035,
                "income_growth": 0.04,
                "development_score": 0.95
            },
            # Dallas
            "75225": {
                "employment_growth": 0.04,
                "population_growth": 0.03,
                "income_growth": 0.05,
                "development_score": 0.9
            },
            "75201": {
                "employment_growth": 0.05,
                "population_growth": 0.04,
                "income_growth": 0.045,
                "development_score": 0.95
            }
        }
    
    def predict_market_trends(
        self,
        zip_code: str,
        current_stats: Dict,
        months_ahead: int = 12
    ) -> Dict:
        """
        Predict market trends for specified months ahead.
        Uses current market stats and economic indicators.
        """
        try:
            # Get market indicators
            indicators = self.market_indicators.get(
                zip_code,
                self._get_default_indicators()
            )
            
            # Prepare feature vector
            features = self._prepare_features(
                current_stats,
                indicators
            )
            
            # Make predictions
            price_change = self._predict_price_change(
                features,
                months_ahead
            )
            trend_metrics = self._predict_market_metrics(
                features,
                months_ahead
            )
            
            # Calculate confidence scores
            confidence = self._calculate_confidence(
                features,
                price_change,
                trend_metrics
            )
            
            return {
                "price_change": price_change,
                "inventory_change": trend_metrics["inventory"],
                "dom_change": trend_metrics["dom"],
                "market_direction": self._get_market_direction(trend_metrics),
                "confidence_score": confidence,
                "prediction_date": datetime.now().isoformat(),
                "months_ahead": months_ahead
            }
            
        except Exception as e:
            print(f"Error predicting market trends: {e}")
            return {}
    
    def analyze_investment_potential(
        self,
        property_data: Dict,
        market_trends: Dict
    ) -> Dict:
        """
        Analyze investment potential for a property.
        Considers both property attributes and market trends.
        """
        try:
            # Calculate base scores
            price_score = self._calculate_price_score(
                property_data,
                market_trends
            )
            location_score = self._calculate_location_score(
                property_data["zip_code"]
            )
            property_score = self._calculate_property_score(
                property_data
            )
            
            # Weight the scores
            weights = {
                "price": 0.4,
                "location": 0.35,
                "property": 0.25
            }
            
            total_score = (
                price_score * weights["price"] +
                location_score * weights["location"] +
                property_score * weights["property"]
            )
            
            return {
                "investment_score": round(total_score * 100),
                "price_score": round(price_score * 100),
                "location_score": round(location_score * 100),
                "property_score": round(property_score * 100),
                "estimated_appreciation": self._estimate_appreciation(
                    property_data,
                    market_trends
                ),
                "risk_level": self._calculate_risk_level(total_score),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error analyzing investment potential: {e}")
            return {}
    
    def _prepare_features(
        self,
        market_stats: Dict,
        indicators: Dict
    ) -> np.ndarray:
        """Prepare feature vector for ML models."""
        features = []
        
        for col in self.feature_columns:
            if col == 'sf_ratio':
                value = market_stats['property_mix'].get('Single Family', 0)
            elif col == 'condo_ratio':
                value = market_stats['property_mix'].get('Condo', 0)
            elif col == 'seasonal_factor':
                month = datetime.now().month
                value = self._get_seasonal_factor(month)
            else:
                value = market_stats.get(col, 0)
            
            features.append(value)
        
        # Add economic indicators
        features.extend([
            indicators['employment_growth'],
            indicators['population_growth'],
            indicators['income_growth'],
            indicators['development_score']
        ])
        
        return np.array(features).reshape(1, -1)
    
    def _predict_price_change(
        self,
        features: np.ndarray,
        months: int
    ) -> float:
        """Predict price change percentage."""
        # Simple model for MVP
        base_change = features[0][-1] * 0.8  # Use development score
        monthly_factor = 1 + (features[0][1] / 12)  # Monthly price trend
        
        return ((monthly_factor ** months) - 1) * 100
    
    def _predict_market_metrics(
        self,
        features: np.ndarray,
        months: int
    ) -> Dict:
        """Predict various market metrics."""
        # Simple predictions for MVP
        inventory_change = features[0][2] * months  # Inventory trend
        dom_change = max(-30, min(30, features[0][3] * 0.1 * months))
        
        return {
            "inventory": inventory_change,
            "dom": dom_change
        }
    
    def _calculate_confidence(
        self,
        features: np.ndarray,
        price_change: float,
        metrics: Dict
    ) -> float:
        """Calculate confidence score for predictions."""
        # Simple confidence calculation for MVP
        base_confidence = 0.7  # Base confidence level
        
        # Adjust based on data quality
        if features[0][-1] > 0.8:  # High development score
            base_confidence += 0.1
        
        # Adjust based on prediction extremity
        if abs(price_change) > 20 or abs(metrics["inventory"]) > 30:
            base_confidence -= 0.1
        
        return max(0.0, min(1.0, base_confidence))
    
    def _get_market_direction(self, metrics: Dict) -> str:
        """Determine market direction based on metrics."""
        if metrics["inventory"] < -10 and metrics["dom"] < -5:
            return "Strong Seller's Market"
        elif metrics["inventory"] < 0 and metrics["dom"] < 0:
            return "Seller's Market"
        elif metrics["inventory"] > 10 and metrics["dom"] > 5:
            return "Strong Buyer's Market"
        elif metrics["inventory"] > 0 and metrics["dom"] > 0:
            return "Buyer's Market"
        else:
            return "Balanced Market"
    
    def _calculate_price_score(
        self,
        property_data: Dict,
        market_trends: Dict
    ) -> float:
        """Calculate price score based on market position."""
        try:
            price = property_data["price"]
            price_change = market_trends["price_change"]
            
            # Price trend factor
            trend_factor = 1 + (price_change / 100)
            
            # Compare to market
            if price_change > 5:  # Growing market
                score = 0.8  # Good baseline
            elif price_change < -5:  # Declining market
                score = 0.4  # Cautious baseline
            else:  # Stable market
                score = 0.6  # Moderate baseline
            
            # Adjust for property price
            if trend_factor > 1.1:  # Strong growth
                score *= 1.2
            elif trend_factor < 0.9:  # Strong decline
                score *= 0.8
            
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5  # Default moderate score
    
    def _calculate_location_score(self, zip_code: str) -> float:
        """Calculate location score based on market indicators."""
        indicators = self.market_indicators.get(
            zip_code,
            self._get_default_indicators()
        )
        
        # Weight the indicators
        weights = {
            "employment_growth": 0.3,
            "population_growth": 0.2,
            "income_growth": 0.25,
            "development_score": 0.25
        }
        
        score = sum(
            indicators[k] * weights[k]
            for k in weights
        )
        
        return max(0.0, min(1.0, score * 2))  # Scale to 0-1
    
    def _calculate_property_score(self, property_data: Dict) -> float:
        """Calculate property score based on attributes."""
        try:
            # Base score from property type
            type_scores = {
                "Single Family": 1.0,
                "Townhouse": 0.8,
                "Condo": 0.7
            }
            
            base_score = type_scores.get(
                property_data["property_type"],
                0.6
            )
            
            # Adjust for age
            year_built = property_data.get("year_built", 1970)
            age_factor = min(1.0, (2024 - year_built) / 50)
            
            # Adjust for size
            sqft = property_data.get("sqft", 0)
            size_factor = min(1.0, sqft / 3000)
            
            # Calculate final score
            score = (
                base_score * 0.4 +
                (1 - age_factor) * 0.3 +
                size_factor * 0.3
            )
            
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5  # Default moderate score
    
    def _estimate_appreciation(
        self,
        property_data: Dict,
        market_trends: Dict
    ) -> Dict:
        """Estimate property appreciation potential."""
        try:
            base_appreciation = market_trends["price_change"]
            
            # Adjust for property type
            type_factors = {
                "Single Family": 1.0,
                "Townhouse": 0.9,
                "Condo": 0.8
            }
            
            type_factor = type_factors.get(
                property_data["property_type"],
                0.7
            )
            
            # Calculate ranges
            conservative = base_appreciation * type_factor * 0.8
            moderate = base_appreciation * type_factor
            optimistic = base_appreciation * type_factor * 1.2
            
            return {
                "conservative": round(conservative, 1),
                "moderate": round(moderate, 1),
                "optimistic": round(optimistic, 1)
            }
            
        except Exception:
            return {
                "conservative": 3.0,
                "moderate": 5.0,
                "optimistic": 7.0
            }
    
    def _calculate_risk_level(self, score: float) -> str:
        """Calculate investment risk level."""
        if score >= 0.8:
            return "Low Risk"
        elif score >= 0.6:
            return "Moderate Risk"
        elif score >= 0.4:
            return "High Risk"
        else:
            return "Very High Risk"
    
    def _get_seasonal_factor(self, month: int) -> float:
        """Get seasonal adjustment factor."""
        factors = {
            1: 0.95,   # January
            2: 0.97,   # February
            3: 1.00,   # March
            4: 1.02,   # April
            5: 1.03,   # May
            6: 1.04,   # June
            7: 1.03,   # July
            8: 1.02,   # August
            9: 1.00,   # September
            10: 0.98,  # October
            11: 0.96,  # November
            12: 0.94   # December
        }
        return factors.get(month, 1.0)
    
    def _get_default_indicators(self) -> Dict:
        """Get default market indicators."""
        return {
            "employment_growth": 0.02,
            "population_growth": 0.015,
            "income_growth": 0.03,
            "development_score": 0.6
        }
