"""
Property comparison engine for identifying similar properties
and investment opportunities.
"""
import numpy as np
from typing import Dict, List, Optional, Tuple
from sklearn.preprocessing import StandardScaler
from sklearn.metrics.pairwise import cosine_similarity

class PropertyComparator:
    """
    Compares properties based on multiple attributes
    and identifies similar investment opportunities.
    """
    
    def __init__(self):
        self.scaler = StandardScaler()
        
        # Feature weights for similarity scoring
        self.feature_weights = {
            "price": 0.25,
            "sqft": 0.20,
            "bedrooms": 0.10,
            "bathrooms": 0.10,
            "year_built": 0.15,
            "lot_size": 0.10,
            "location_score": 0.10
        }
        
        # Location scoring factors
        self.location_factors = {
            # Nashville
            "37215": 0.90,  # Belle Meade/Green Hills
            "37203": 0.85,  # Downtown/Midtown
            # Atlanta
            "30305": 0.88,  # Buckhead
            "30308": 0.82,  # Midtown
            # Dallas
            "75225": 0.92,  # Highland Park
            "75201": 0.86   # Downtown
        }
        
        # Property type adjustments
        self.type_adjustments = {
            "Single Family": {
                "price": 1.0,
                "sqft": 1.0,
                "lot_size": 1.0
            },
            "Townhouse": {
                "price": 0.9,
                "sqft": 0.85,
                "lot_size": 0.7
            },
            "Condo": {
                "price": 0.85,
                "sqft": 0.8,
                "lot_size": 0.5
            }
        }
    
    def find_similar_properties(
        self,
        target_property: Dict,
        comparison_pool: List[Dict],
        min_similarity: float = 0.7
    ) -> List[Dict]:
        """
        Find similar properties based on multiple attributes.
        Returns list of properties with similarity scores.
        """
        try:
            if not comparison_pool:
                return []
            
            # Extract and normalize features
            target_features = self._extract_features(target_property)
            pool_features = [
                self._extract_features(p)
                for p in comparison_pool
            ]
            
            # Calculate similarities
            similarities = self._calculate_similarities(
                target_features,
                pool_features
            )
            
            # Filter and rank results
            similar_properties = []
            for i, similarity in enumerate(similarities):
                if similarity >= min_similarity:
                    property_data = comparison_pool[i].copy()
                    property_data["similarity_score"] = round(
                        similarity * 100,
                        1
                    )
                    similar_properties.append(property_data)
            
            # Sort by similarity score
            similar_properties.sort(
                key=lambda x: x["similarity_score"],
                reverse=True
            )
            
            return similar_properties
            
        except Exception as e:
            print(f"Error finding similar properties: {e}")
            return []
    
    def analyze_price_competitiveness(
        self,
        property_data: Dict,
        market_comps: List[Dict]
    ) -> Dict:
        """
        Analyze price competitiveness against market comps.
        Returns price analysis and recommendations.
        """
        try:
            if not market_comps:
                return self._get_default_price_analysis()
            
            # Calculate price per sqft
            target_ppsf = property_data["price"] / property_data["sqft"]
            comp_ppsf = [
                p["price"] / p["sqft"]
                for p in market_comps
            ]
            
            # Adjust for property type
            target_type = property_data.get(
                "property_type",
                "Single Family"
            )
            type_factor = self.type_adjustments[target_type]["price"]
            
            # Calculate statistics
            median_ppsf = np.median(comp_ppsf)
            std_ppsf = np.std(comp_ppsf)
            
            # Determine price position
            z_score = (target_ppsf - median_ppsf) / std_ppsf
            
            return {
                "price_per_sqft": round(target_ppsf, 2),
                "median_market_ppsf": round(median_ppsf, 2),
                "price_position": self._get_price_position(z_score),
                "percent_difference": round(
                    ((target_ppsf / median_ppsf) - 1) * 100,
                    1
                ),
                "adjusted_value": round(
                    median_ppsf * property_data["sqft"] * type_factor,
                    -3
                ),
                "confidence_score": self._calculate_comp_confidence(
                    market_comps
                )
            }
            
        except Exception as e:
            print(f"Error analyzing price competitiveness: {e}")
            return self._get_default_price_analysis()
    
    def calculate_investment_comparisons(
        self,
        target_property: Dict,
        similar_properties: List[Dict]
    ) -> Dict:
        """
        Calculate investment metrics compared to similar properties.
        Returns comparative investment analysis.
        """
        try:
            if not similar_properties:
                return self._get_default_investment_comparison()
            
            # Calculate key metrics
            target_metrics = self._calculate_investment_metrics(
                target_property
            )
            comp_metrics = [
                self._calculate_investment_metrics(p)
                for p in similar_properties
            ]
            
            # Compare metrics
            metric_comparisons = {}
            for metric in target_metrics:
                comp_values = [m[metric] for m in comp_metrics]
                metric_comparisons[metric] = {
                    "value": target_metrics[metric],
                    "market_median": np.median(comp_values),
                    "market_std": np.std(comp_values),
                    "percentile": stats.percentileofscore(
                        comp_values,
                        target_metrics[metric]
                    )
                }
            
            return {
                "metrics": metric_comparisons,
                "overall_position": self._calculate_investment_position(
                    metric_comparisons
                ),
                "confidence_score": self._calculate_metric_confidence(
                    similar_properties
                )
            }
            
        except Exception as e:
            print(f"Error calculating investment comparisons: {e}")
            return self._get_default_investment_comparison()
    
    def _extract_features(self, property_data: Dict) -> np.ndarray:
        """Extract and normalize property features."""
        features = []
        
        for feature, weight in self.feature_weights.items():
            if feature == "location_score":
                value = self.location_factors.get(
                    property_data.get("zip_code", "00000"),
                    0.5
                )
            else:
                value = float(property_data.get(feature, 0))
            
            features.append(value * weight)
        
        return np.array(features)
    
    def _calculate_similarities(
        self,
        target: np.ndarray,
        pool: List[np.ndarray]
    ) -> np.ndarray:
        """Calculate similarity scores between properties."""
        pool_array = np.array(pool)
        similarities = cosine_similarity(
            target.reshape(1, -1),
            pool_array
        )
        return similarities[0]
    
    def _calculate_investment_metrics(
        self,
        property_data: Dict
    ) -> Dict:
        """Calculate investment metrics for a property."""
        price = property_data.get("price", 0)
        sqft = property_data.get("sqft", 0)
        year_built = property_data.get("year_built", 1970)
        
        return {
            "price_per_sqft": price / sqft if sqft else 0,
            "age_factor": (2024 - year_built) / 50,
            "size_value_ratio": sqft / (price / 1000) if price else 0
        }
    
    def _get_price_position(self, z_score: float) -> str:
        """Determine price position in market."""
        if z_score < -2:
            return "Significantly Underpriced"
        elif z_score < -1:
            return "Underpriced"
        elif z_score < 1:
            return "Fairly Priced"
        elif z_score < 2:
            return "Overpriced"
        else:
            return "Significantly Overpriced"
    
    def _calculate_comp_confidence(
        self,
        comps: List[Dict]
    ) -> float:
        """Calculate confidence score for comp analysis."""
        if len(comps) < 3:
            return 0.5
        
        # Adjust for number of comps
        base_confidence = min(1.0, len(comps) / 10)
        
        # Adjust for comp similarity
        similarity_scores = [
            c.get("similarity_score", 0) / 100
            for c in comps
        ]
        avg_similarity = np.mean(similarity_scores)
        
        return base_confidence * avg_similarity
    
    def _calculate_investment_position(
        self,
        metric_comparisons: Dict
    ) -> str:
        """Calculate overall investment position."""
        percentiles = [
            m["percentile"]
            for m in metric_comparisons.values()
        ]
        avg_percentile = np.mean(percentiles)
        
        if avg_percentile >= 80:
            return "Top Investment Opportunity"
        elif avg_percentile >= 60:
            return "Strong Investment"
        elif avg_percentile >= 40:
            return "Average Investment"
        elif avg_percentile >= 20:
            return "Below Average Investment"
        else:
            return "Poor Investment"
    
    def _calculate_metric_confidence(
        self,
        similar_properties: List[Dict]
    ) -> float:
        """Calculate confidence in metric comparisons."""
        if len(similar_properties) < 3:
            return 0.5
        
        # Base confidence on sample size
        base_confidence = min(1.0, len(similar_properties) / 10)
        
        # Adjust for similarity scores
        similarity_scores = [
            p.get("similarity_score", 0) / 100
            for p in similar_properties
        ]
        avg_similarity = np.mean(similarity_scores)
        
        return base_confidence * avg_similarity
    
    def _get_default_price_analysis(self) -> Dict:
        """Get default price analysis."""
        return {
            "price_per_sqft": 0,
            "median_market_ppsf": 0,
            "price_position": "Unknown",
            "percent_difference": 0,
            "adjusted_value": 0,
            "confidence_score": 0
        }
    
    def _get_default_investment_comparison(self) -> Dict:
        """Get default investment comparison."""
        return {
            "metrics": {},
            "overall_position": "Unknown",
            "confidence_score": 0
        }
