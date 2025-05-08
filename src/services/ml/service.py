from typing import Dict, List, Optional
import numpy as np
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
import joblib
import logging
import os
from datetime import datetime

from ...utils.metrics import track_execution_time
from ...config import get_settings

logger = logging.getLogger(__name__)

class MLService:
    def __init__(self, config: Dict):
        self.config = config
        self.models = {}
        self.scalers = {}
        self.vectorizers = {}
        self.load_models()
        
    def load_models(self):
        """Load ML models and preprocessors."""
        model_path = self.config.get("model_path", "models")
        try:
            # Load property valuation model
            if os.path.exists(f"{model_path}/valuation_model.joblib"):
                self.models["valuation"] = joblib.load(f"{model_path}/valuation_model.joblib")
                self.scalers["valuation"] = joblib.load(f"{model_path}/valuation_scaler.joblib")
                
            # Load market prediction model
            if os.path.exists(f"{model_path}/market_model.joblib"):
                self.models["market"] = joblib.load(f"{model_path}/market_model.joblib")
                self.scalers["market"] = joblib.load(f"{model_path}/market_scaler.joblib")
                
            # Load text vectorizer for amenity analysis
            if os.path.exists(f"{model_path}/amenity_vectorizer.joblib"):
                self.vectorizers["amenity"] = joblib.load(f"{model_path}/amenity_vectorizer.joblib")
                
        except Exception as e:
            logger.error(f"Error loading models: {str(e)}")
            
    @track_execution_time
    async def predict_property_value(self, features: Dict) -> Dict:
        """Predict property value using ML model."""
        try:
            if "valuation" not in self.models:
                return {"error": "Valuation model not loaded"}
                
            # Prepare features
            X = self._prepare_valuation_features(features)
            
            # Make prediction
            value = self.models["valuation"].predict(X)[0]
            confidence = self._calculate_prediction_confidence(self.models["valuation"], X)
            
            return {
                "estimated_value": float(value),
                "confidence_score": float(confidence),
                "factors": self._get_value_factors(self.models["valuation"], X),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Prediction error: {str(e)}")
            return {"error": str(e)}
            
    @track_execution_time
    async def predict_market_trends(self, market_data: Dict) -> Dict:
        """Predict market trends using ML model."""
        try:
            if "market" not in self.models:
                return {"error": "Market model not loaded"}
                
            # Prepare features
            X = self._prepare_market_features(market_data)
            
            # Make predictions
            trends = self.models["market"].predict(X)
            confidence = self._calculate_prediction_confidence(self.models["market"], X)
            
            return {
                "price_trend": float(trends[0]),
                "demand_trend": float(trends[1]),
                "confidence_score": float(confidence),
                "factors": self._get_trend_factors(self.models["market"], X),
                "timestamp": datetime.utcnow().isoformat()
            }
        except Exception as e:
            logger.error(f"Trend prediction error: {str(e)}")
            return {"error": str(e)}
            
    def _prepare_valuation_features(self, features: Dict) -> np.ndarray:
        """Prepare features for valuation model."""
        # Extract and scale numerical features
        numerical = [
            features.get("square_feet", 0),
            features.get("bedrooms", 0),
            features.get("bathrooms", 0),
            features.get("lot_size", 0),
            features.get("year_built", 2000)
        ]
        
        # Process amenities if available
        if "amenities" in features and "amenity" in self.vectorizers:
            amenity_features = self.vectorizers["amenity"].transform([" ".join(features["amenities"])])
            return np.hstack([
                self.scalers["valuation"].transform([numerical]),
                amenity_features.toarray()
            ])
        
        return self.scalers["valuation"].transform([numerical])
        
    def _prepare_market_features(self, market_data: Dict) -> np.ndarray:
        """Prepare features for market prediction."""
        features = [
            market_data.get("current_price", 0),
            market_data.get("price_change", 0),
            market_data.get("inventory", 0),
            market_data.get("days_on_market", 0),
            market_data.get("sales_volume", 0)
        ]
        return self.scalers["market"].transform([features])
        
    def _calculate_prediction_confidence(self, model, X: np.ndarray) -> float:
        """Calculate confidence score for prediction."""
        if hasattr(model, "predict_proba"):
            proba = model.predict_proba(X)
            return float(np.max(proba))
        return 0.85  # Default confidence if model doesn't support probabilities
        
    def _get_value_factors(self, model, X: np.ndarray) -> Dict[str, float]:
        """Get feature importance for valuation."""
        if hasattr(model, "feature_importances_"):
            return {f"factor_{i}": float(imp) 
                   for i, imp in enumerate(model.feature_importances_)}
        return {}
        
    def _get_trend_factors(self, model, X: np.ndarray) -> Dict[str, float]:
        """Get feature importance for market trends."""
        if hasattr(model, "feature_importances_"):
            return {f"factor_{i}": float(imp) 
                   for i, imp in enumerate(model.feature_importances_)}
        return {}
