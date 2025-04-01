"""
Lead scoring module implementing ML-based analysis for property leads.
Integrates with our hybrid data approach and API Gateway.
"""
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import logging

@dataclass
class LeadScore:
    motivation_score: float
    deal_probability: float
    response_likelihood: float
    confidence_score: float
    timestamp: datetime
    features_used: List[str]

class LeadScorer:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.scaler = StandardScaler()
        self.value_scaler = MinMaxScaler()
        
        # Initialize models
        self.motivation_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.deal_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        self.response_model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42
        )
        
        # Feature definitions with normalization ranges
        self.property_features = [
            "estimated_value",      # Normalize based on market median
            "last_sale_price",      # Normalize based on market median
            "last_sale_date",       # Convert to years and normalize
            "tax_assessment",       # Normalize based on market median
            "years_owned",          # Max 30 years
            "equity_percentage",    # Already 0-1
            "tax_status",          # Categorical
            "property_condition",   # Categorical
            "occupancy_status"      # Categorical
        ]
        
        self.market_features = [
            "median_price",        # Use as baseline for normalization
            "price_trend",         # Already -1 to 1
            "days_on_market",      # Max 365 days
            "inventory_level",     # Categorical
            "market_strength"      # Already 0-1
        ]
        
        self.owner_features = [
            "age",                # Normalize 18-100
            "income_level",       # Categorical
            "property_count",     # Max 10
            "bankruptcy_history", # Boolean
            "foreclosure_history", # Boolean
            "tax_liens",         # Boolean
            "mailing_address_match" # Boolean
        ]
        
        # Value normalization parameters
        self.value_ranges = {
            "age": (18, 100),
            "years_owned": (0, 30),
            "days_on_market": (0, 365),
            "property_count": (0, 10)
        }
        
        # Categorical mappings
        self.categorical_mappings = {
            "property_condition": {
                "excellent": 1.0,
                "good": 0.75,
                "fair": 0.5,
                "poor": 0.25,
                "very_poor": 0.0
            },
            "tax_status": {
                "current": 1.0,
                "delinquent": 0.0,
                "partial": 0.5
            },
            "occupancy_status": {
                "owner_occupied": 1.0,
                "tenant_occupied": 0.5,
                "vacant": 0.0
            },
            "inventory_level": {
                "very_low": 1.0,
                "low": 0.75,
                "moderate": 0.5,
                "high": 0.25,
                "very_high": 0.0
            },
            "income_level": {
                "high": 1.0,
                "medium_high": 0.75,
                "medium": 0.5,
                "medium_low": 0.25,
                "low": 0.0
            }
        }
    
    def score_lead(
        self,
        property_data: Dict,
        market_data: Dict,
        owner_data: Dict
    ) -> LeadScore:
        """
        Score a lead based on property, market, and owner data.
        Uses our hybrid approach, working with both mock and ATTOM data.
        """
        try:
            # 1. Extract and normalize features
            features, used_features = self._extract_features(
                property_data,
                market_data,
                owner_data
            )
            
            if len(features) == 0:
                raise ValueError("No valid features found for scoring")
            
            # 2. Generate predictions
            motivation = self._predict_motivation(features)
            deal_prob = self._predict_deal_probability(features)
            response = self._predict_response_likelihood(features)
            
            # 3. Calculate confidence score
            confidence = self._calculate_confidence(
                used_features,
                motivation,
                deal_prob,
                response
            )
            
            return LeadScore(
                motivation_score=motivation,
                deal_probability=deal_prob,
                response_likelihood=response,
                confidence_score=confidence,
                timestamp=datetime.now(),
                features_used=used_features
            )
            
        except Exception as e:
            self.logger.error(f"Lead scoring error: {e}")
            return self._get_fallback_score(str(e))
    
    def _extract_features(
        self,
        property_data: Dict,
        market_data: Dict,
        owner_data: Dict
    ) -> Tuple[np.ndarray, List[str]]:
        """Extract and normalize features from input data."""
        features = []
        used_features = []
        
        try:
            # Get market median for value normalization
            market_median = float(market_data.get("median_price", 0))
            if market_median == 0:
                # Fallback to property value if no market data
                market_median = float(property_data.get("estimated_value", 500000))
            
            # Property features
            for feature in self.property_features:
                value = property_data.get(feature)
                if value is not None:
                    norm_value = self._normalize_feature(
                        feature,
                        value,
                        market_median
                    )
                    if norm_value is not None:
                        features.append(norm_value)
                        used_features.append(feature)
            
            # Market features
            for feature in self.market_features:
                value = market_data.get(feature)
                if value is not None:
                    norm_value = self._normalize_feature(
                        feature,
                        value,
                        market_median
                    )
                    if norm_value is not None:
                        features.append(norm_value)
                        used_features.append(feature)
            
            # Owner features
            for feature in self.owner_features:
                value = owner_data.get(feature)
                if value is not None:
                    norm_value = self._normalize_feature(
                        feature,
                        value,
                        market_median
                    )
                    if norm_value is not None:
                        features.append(norm_value)
                        used_features.append(feature)
            
            if not features:
                return np.array([]).reshape(1, 0), []
            
            return np.array(features).reshape(1, -1), used_features
            
        except Exception as e:
            self.logger.error(f"Feature extraction error: {e}")
            return np.array([]).reshape(1, 0), []
    
    def _normalize_feature(
        self,
        feature_name: str,
        value: Any,
        market_median: float
    ) -> Optional[float]:
        """Normalize feature value based on feature type and context."""
        try:
            # Handle boolean values
            if isinstance(value, bool):
                return float(value)
            
            # Handle numeric values
            if isinstance(value, (int, float)):
                # Value-based features
                if feature_name in ["estimated_value", "last_sale_price", "tax_assessment"]:
                    if market_median > 0:
                        return min(float(value) / market_median, 2.0)
                    return 0.5
                
                # Range-based features
                if feature_name in self.value_ranges:
                    min_val, max_val = self.value_ranges[feature_name]
                    return max(0.0, min(1.0, (float(value) - min_val) / (max_val - min_val)))
                
                # Percentage-based features
                if feature_name in ["equity_percentage", "market_strength", "price_trend"]:
                    return max(-1.0, min(1.0, float(value)))
                
                # Default normalization for unknown numeric features
                return max(0.0, min(1.0, float(value)))
            
            # Handle string values
            if isinstance(value, str):
                # Handle date values
                if feature_name == "last_sale_date":
                    try:
                        sale_date = datetime.strptime(value, "%Y-%m-%d")
                        years = (datetime.now() - sale_date).days / 365.25
                        return max(0.0, min(1.0, years / 30.0))  # Normalize to 30 years
                    except:
                        return 0.5
                
                # Handle categorical values
                value_lower = value.lower()
                if feature_name in self.categorical_mappings:
                    return self.categorical_mappings[feature_name].get(value_lower, 0.5)
                
                # Boolean-like strings
                if value_lower in ["yes", "true", "active"]:
                    return 1.0
                if value_lower in ["no", "false", "inactive"]:
                    return 0.0
            
            # Default normalization for unknown types
            return 0.5
            
        except Exception as e:
            self.logger.warning(f"Feature normalization error: {e}")
            return None
    
    def _predict_motivation(self, features: np.ndarray) -> float:
        """Predict owner motivation score."""
        try:
            # For MVP, use simplified scoring
            # Will be replaced with trained model predictions
            weights = np.random.uniform(0.4, 0.6, features.shape[1])
            score = np.dot(features, weights)[0]
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"Motivation prediction error: {e}")
            return 0.5
    
    def _predict_deal_probability(self, features: np.ndarray) -> float:
        """Predict probability of successful deal."""
        try:
            # For MVP, use simplified scoring
            # Will be replaced with trained model predictions
            weights = np.random.uniform(0.4, 0.6, features.shape[1])
            score = np.dot(features, weights)[0]
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"Deal probability prediction error: {e}")
            return 0.5
    
    def _predict_response_likelihood(self, features: np.ndarray) -> float:
        """Predict likelihood of owner response."""
        try:
            # For MVP, use simplified scoring
            # Will be replaced with trained model predictions
            weights = np.random.uniform(0.4, 0.6, features.shape[1])
            score = np.dot(features, weights)[0]
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            self.logger.error(f"Response likelihood prediction error: {e}")
            return 0.5
    
    def _calculate_confidence(
        self,
        used_features: List[str],
        motivation: float,
        deal_prob: float,
        response: float
    ) -> float:
        """Calculate confidence score based on available data and predictions."""
        try:
            # Calculate feature coverage for each category
            total_features = len(self.property_features) + len(self.market_features) + len(self.owner_features)
            feature_coverage = len(used_features) / total_features
            
            # Calculate category coverage
            property_coverage = len([f for f in used_features if f in self.property_features]) / len(self.property_features)
            market_coverage = len([f for f in used_features if f in self.market_features]) / len(self.market_features)
            owner_coverage = len([f for f in used_features if f in self.owner_features]) / len(self.owner_features)
            
            # Weight category coverage
            category_confidence = (
                0.4 * property_coverage +
                0.3 * market_coverage +
                0.3 * owner_coverage
            )
            
            # Prediction confidence based on extreme values
            prediction_confidence = 1.0 - (
                abs(motivation - 0.5) +
                abs(deal_prob - 0.5) +
                abs(response - 0.5)
            ) / 3
            
            # Combine scores with weights
            confidence = (
                0.4 * feature_coverage +
                0.4 * category_confidence +
                0.2 * prediction_confidence
            )
            
            return max(0.0, min(1.0, confidence))
            
        except Exception as e:
            self.logger.error(f"Confidence calculation error: {e}")
            return 0.5
    
    def _get_fallback_score(self, error: str) -> LeadScore:
        """Generate fallback score when scoring fails."""
        return LeadScore(
            motivation_score=0.5,
            deal_probability=0.5,
            response_likelihood=0.5,
            confidence_score=0.1,
            timestamp=datetime.now(),
            features_used=[]
        )
