"""
ML model plugin for property valuation and price prediction.
"""
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from tensorflow import keras
from tensorflow.keras import layers

from src.core.plugin_system import ModelPlugin

logger = logging.getLogger(__name__)

class PropertyValuationModel(ModelPlugin):
    """ML model for property valuation and analysis"""
    
    def __init__(self):
        self.model = None
        self.preprocessor = None
        self.feature_cols = None
        self.config = None
        
    def initialize(self, config: Dict) -> bool:
        """Initialize the model with configuration"""
        try:
            self.config = config
            
            # Set up feature columns based on config
            self.feature_cols = self._setup_feature_columns()
            
            # Create preprocessor
            self.preprocessor = self._create_preprocessor()
            
            # Create or load model
            if config['model_type'] == 'advanced':
                self.model = self._create_advanced_model()
            else:
                self.model = self._create_basic_model()
                
            # Load weights if they exist
            model_path = Path(config['model_path'])
            if model_path.exists():
                self.model.load_weights(str(model_path))
                
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize valuation model: {str(e)}")
            return False
            
    def get_capabilities(self) -> List[str]:
        """Get list of model capabilities"""
        return ['price_prediction', 'value_analysis', 'risk_assessment']
        
    def process(self, data: Dict) -> Dict:
        """Process property data for prediction"""
        try:
            # Extract features
            features = self._extract_features(data)
            
            # Make prediction
            prediction = self.predict({'features': features})
            
            # Add analysis
            analysis = self._analyze_prediction(data, prediction)
            
            return {
                'prediction': prediction,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error processing property data: {str(e)}")
            return data
            
    async def predict(self, data: Dict) -> Dict:
        """Make price predictions"""
        try:
            features = data['features']
            
            # Preprocess features
            X = self.preprocessor.transform(pd.DataFrame([features]))
            
            # Make prediction
            pred = self.model.predict(X)[0]
            
            confidence = self._calculate_confidence(features)
            
            return {
                'predicted_price': float(pred),
                'confidence': confidence,
                'timestamp': pd.Timestamp.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error making prediction: {str(e)}")
            return {}
            
    def get_model_info(self) -> Dict:
        """Get information about the model"""
        return {
            'type': self.config['model_type'],
            'features': self.feature_cols,
            'architecture': self.model.summary() if self.model else None,
            'config': self.config
        }
        
    def _setup_feature_columns(self) -> Dict[str, List[str]]:
        """Set up feature columns based on configuration"""
        features = {
            'numeric': [
                'square_feet',
                'bedrooms',
                'bathrooms',
                'year_built',
                'lot_size'
            ],
            'categorical': [
                'property_type',
                'condition'
            ]
        }
        
        if self.config['feature_engineering']['use_market_features']:
            features['numeric'].extend([
                'median_price',
                'price_trend',
                'days_on_market'
            ])
            
        if self.config['feature_engineering']['use_location_features']:
            features['numeric'].extend([
                'latitude',
                'longitude'
            ])
            features['categorical'].extend([
                'neighborhood',
                'school_district'
            ])
            
        return features
        
    def _create_preprocessor(self) -> ColumnTransformer:
        """Create feature preprocessing pipeline"""
        numeric_features = self.feature_cols['numeric']
        categorical_features = self.feature_cols['categorical']
        
        numeric_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='median')),
            ('scaler', StandardScaler())
        ])
        
        categorical_transformer = Pipeline(steps=[
            ('imputer', SimpleImputer(strategy='constant', fill_value='missing')),
            ('onehot', OneHotEncoder(drop='first', sparse=False))
        ])
        
        preprocessor = ColumnTransformer(
            transformers=[
                ('num', numeric_transformer, numeric_features),
                ('cat', categorical_transformer, categorical_features)
            ])
            
        return preprocessor
        
    def _create_basic_model(self) -> keras.Model:
        """Create basic neural network model"""
        model = keras.Sequential([
            layers.Dense(64, activation='relu'),
            layers.Dropout(0.2),
            layers.Dense(32, activation='relu'),
            layers.Dense(1)
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
        
    def _create_advanced_model(self) -> keras.Model:
        """Create advanced neural network model"""
        # Input layers
        numeric_input = keras.Input(shape=(len(self.feature_cols['numeric']),))
        categorical_input = keras.Input(shape=(len(self.feature_cols['categorical']),))
        
        # Process numeric features
        x1 = layers.Dense(64, activation='relu')(numeric_input)
        x1 = layers.Dropout(0.2)(x1)
        
        # Process categorical features
        x2 = layers.Dense(32, activation='relu')(categorical_input)
        x2 = layers.Dropout(0.2)(x2)
        
        # Combine features
        combined = layers.concatenate([x1, x2])
        
        # Deep layers
        x = layers.Dense(128, activation='relu')(combined)
        x = layers.Dropout(0.3)(x)
        x = layers.Dense(64, activation='relu')(x)
        x = layers.Dropout(0.2)(x)
        x = layers.Dense(32, activation='relu')(x)
        
        # Output layer
        output = layers.Dense(1)(x)
        
        # Create model
        model = keras.Model(
            inputs=[numeric_input, categorical_input],
            outputs=output
        )
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
        
    def _extract_features(self, data: Dict) -> Dict:
        """Extract features from property data"""
        features = {}
        
        # Extract numeric features
        for col in self.feature_cols['numeric']:
            features[col] = data.get(col, 0)
            
        # Extract categorical features
        for col in self.feature_cols['categorical']:
            features[col] = str(data.get(col, 'unknown'))
            
        return features
        
    def _calculate_confidence(self, features: Dict) -> float:
        """Calculate prediction confidence"""
        # Simple heuristic based on feature completeness
        total_features = len(self.feature_cols['numeric']) + len(self.feature_cols['categorical'])
        present_features = sum(1 for f in features.values() if f not in (None, 0, 'unknown'))
        
        return min(0.95, present_features / total_features)
        
    def _analyze_prediction(self, data: Dict, prediction: Dict) -> Dict:
        """Analyze prediction results"""
        actual_price = data.get('price', 0)
        predicted_price = prediction['predicted_price']
        
        analysis = {
            'price_difference': actual_price - predicted_price if actual_price else 0,
            'price_ratio': actual_price / predicted_price if actual_price and predicted_price else 1,
            'confidence': prediction['confidence'],
            'risk_level': self._assess_risk(data, prediction)
        }
        
        return analysis
        
    def _assess_risk(self, data: Dict, prediction: Dict) -> str:
        """Assess investment risk level"""
        confidence = prediction['confidence']
        price_ratio = data.get('price', 0) / prediction['predicted_price'] if prediction['predicted_price'] else 1
        
        if confidence < 0.5:
            return 'high'
        elif confidence < 0.7:
            return 'medium'
        elif price_ratio > 1.2:
            return 'medium'
        else:
            return 'low'
