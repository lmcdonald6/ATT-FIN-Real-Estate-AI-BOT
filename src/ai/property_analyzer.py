"""
Advanced property analysis and recommendation system.
Implements NLP, recommendation algorithms, and data preprocessing techniques.
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import StandardScaler
import pandas as pd
import logging

logger = logging.getLogger(__name__)

class PropertyAnalyzer:
    """Advanced property analysis using ML techniques"""
    
    def __init__(self):
        self.tfidf = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 2)
        )
        self.svd = TruncatedSVD(n_components=3)  # Reduced components
        self.scaler = StandardScaler()
        
    def preprocess_property_data(self, properties: List[Dict]) -> pd.DataFrame:
        """Preprocess property data with advanced cleaning and feature engineering"""
        if not properties:
            raise ValueError("No properties provided")
            
        try:
            df = pd.DataFrame(properties)
            
            # Handle missing values
            numeric_cols = ['price', 'sqft', 'bedrooms', 'bathrooms']
            for col in numeric_cols:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                    # Fix pandas warning by using direct assignment
                    df[col] = df[col].fillna(df[col].median())
            
            # Feature engineering
            if all(col in df.columns for col in ['price', 'sqft']):
                df['price_per_sqft'] = df['price'] / df['sqft']
                
            # Detect and handle outliers
            for col in numeric_cols:
                if col in df.columns:
                    q1 = df[col].quantile(0.25)
                    q3 = df[col].quantile(0.75)
                    iqr = q3 - q1
                    lower_bound = q1 - (1.5 * iqr)
                    upper_bound = q3 + (1.5 * iqr)
                    df[f'{col}_is_outlier'] = ~df[col].between(lower_bound, upper_bound)
            
            return df
            
        except Exception as e:
            logger.error(f"Error preprocessing property data: {str(e)}")
            raise ValueError(f"Error preprocessing property data: {str(e)}")
            
    def analyze_description_sentiment(self, description: str) -> Dict[str, float]:
        """Analyze sentiment and key features from property description"""
        if not description:
            raise ValueError("Empty description provided")
            
        try:
            # Extract key features using TF-IDF
            features = self.tfidf.fit_transform([description])
            
            # Get top features
            feature_names = self.tfidf.get_feature_names_out()
            top_features = pd.DataFrame(
                features.toarray(),
                columns=feature_names
            ).T.sort_values(by=0, ascending=False)
            
            return {
                'key_features': top_features.head(5).index.tolist(),
                'feature_importance': top_features.head(5)[0].tolist()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing description: {str(e)}")
            raise ValueError(f"Error analyzing description: {str(e)}")
            
    def find_similar_properties(
        self,
        target_property: Dict,
        all_properties: List[Dict],
        n_similar: int = 5
    ) -> List[Dict]:
        """Find similar properties using SVD-based similarity"""
        if not target_property or not all_properties:
            raise ValueError("Invalid property data")
            
        try:
            # Convert properties to DataFrame
            df = self.preprocess_property_data(all_properties)
            
            # Prepare feature matrix
            feature_cols = ['price', 'sqft', 'bedrooms', 'bathrooms']
            if 'price_per_sqft' in df.columns:
                feature_cols.append('price_per_sqft')
                
            feature_matrix = df[feature_cols].values
            
            # Scale features
            scaled_features = self.scaler.fit_transform(feature_matrix)
            
            # Adjust SVD components
            n_components = min(3, scaled_features.shape[1])
            self.svd.n_components = n_components
            
            # Apply SVD
            latent_features = self.svd.fit_transform(scaled_features)
            
            # Find target property index
            target_idx = next(
                (i for i, p in enumerate(all_properties)
                if p.get('id') == target_property.get('id')),
                0  # Default to first property if not found
            )
            
            # Calculate similarities
            target_vector = latent_features[target_idx]
            similarities = np.dot(latent_features, target_vector)
            similar_indices = np.argsort(similarities)[::-1][1:n_similar+1]
            
            return [all_properties[i] for i in similar_indices]
            
        except Exception as e:
            logger.error(f"Error finding similar properties: {str(e)}")
            raise ValueError(f"Error finding similar properties: {str(e)}")
            
    def get_property_insights(self, property_data: Dict) -> Dict:
        """Generate comprehensive insights about a property"""
        if not property_data:
            raise ValueError("No property data provided")
            
        try:
            insights = {
                'sentiment': self.analyze_description_sentiment(
                    property_data.get('description', '')
                ),
                'price_analysis': {},
                'location_score': 0.0,
                'investment_potential': 0.0
            }
            
            # Price analysis
            if 'price' in property_data and 'sqft' in property_data:
                price_per_sqft = property_data['price'] / property_data['sqft']
                insights['price_analysis'] = {
                    'price_per_sqft': price_per_sqft,
                    'is_good_value': price_per_sqft < 200  # Threshold should be dynamic
                }
            
            # Location score (placeholder for more complex analysis)
            if 'location' in property_data:
                # This should integrate with external APIs for real data
                insights['location_score'] = 0.8  # Example score
            
            # Investment potential (placeholder for more complex analysis)
            if all(k in property_data for k in ['price', 'rent_estimate']):
                cap_rate = (property_data['rent_estimate'] * 12) / property_data['price']
                insights['investment_potential'] = cap_rate
            
            return insights
            
        except Exception as e:
            logger.error(f"Error generating property insights: {str(e)}")
            raise ValueError(f"Error generating property insights: {str(e)}")
