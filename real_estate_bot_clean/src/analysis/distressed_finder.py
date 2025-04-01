"""
Distressed property finder module that works with our hybrid data approach
(mock + selective ATTOM API enrichment).
"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

class DistressedFinder:
    def __init__(self):
        # Distress indicators and weights
        self.indicators = {
            "tax_delinquent": 0.3,
            "foreclosure_status": 0.25,
            "vacancy_status": 0.15,
            "maintenance_issues": 0.1,
            "owner_circumstances": 0.1,
            "market_position": 0.1
        }
        
        # Default thresholds
        self.thresholds = {
            "high_potential": 0.75,
            "medium_potential": 0.5,
            "low_potential": 0.25
        }
        
        # Initialize ML model for distress prediction
        self.distress_model = RandomForestClassifier(
            n_estimators=100,
            random_state=42
        )
        
        # Initialize with mock training data
        self._initialize_model()
    
    def analyze_property(
        self,
        property_data: Dict,
        market_data: Optional[Dict] = None
    ) -> Dict:
        """
        Analyze a property for distress indicators.
        Uses hybrid approach - mock data enriched with ATTOM when available.
        """
        try:
            # Handle empty data
            if not property_data:
                return self._get_default_analysis()
            
            # Extract base features
            features = self._extract_features(property_data, market_data)
            
            # Calculate distress score
            distress_score = self._calculate_distress_score(features)
            
            # Get opportunity level
            opportunity_level = self._get_opportunity_level(distress_score)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                features,
                distress_score
            )
            
            return {
                "property_id": property_data.get("id", ""),
                "distress_score": round(distress_score, 2),
                "opportunity_level": opportunity_level,
                "indicators": features,
                "recommendations": recommendations,
                "confidence_score": self._calculate_confidence(
                    property_data,
                    features
                )
            }
            
        except Exception as e:
            print(f"Error analyzing property: {e}")
            return self._get_default_analysis()
    
    def _initialize_model(self):
        """Initialize model with mock training data."""
        try:
            # Generate mock training data
            n_samples = 1000
            n_features = len(self.indicators)
            
            # Generate features
            X = np.random.rand(n_samples, n_features)
            
            # Generate labels (0: not distressed, 1: distressed)
            y = (np.mean(X * list(self.indicators.values()), axis=1) > 0.6).astype(int)
            
            # Fit model
            self.distress_model.fit(X, y)
            
        except Exception as e:
            print(f"Error initializing distress model: {e}")
            return self._get_default_analysis()
    
    def _extract_features(
        self,
        property_data: Dict,
        market_data: Optional[Dict]
    ) -> Dict:
        """Extract distress features from property data."""
        try:
            # Handle empty data
            if not property_data:
                return {}
            
            features = {}
            
            # Tax status (from ATTOM if available)
            if "attom_data" in property_data:
                tax_data = property_data["attom_data"].get("tax", {})
                features["tax_delinquent"] = tax_data.get(
                    "is_delinquent",
                    self._mock_tax_status()
                )
            else:
                features["tax_delinquent"] = self._mock_tax_status()
            
            # Foreclosure status
            features["foreclosure_status"] = self._get_foreclosure_status(
                property_data
            )
            
            # Vacancy analysis
            features["vacancy_status"] = self._analyze_vacancy(
                property_data
            )
            
            # Maintenance issues
            features["maintenance_issues"] = self._assess_maintenance(
                property_data
            )
            
            # Owner circumstances
            features["owner_circumstances"] = self._analyze_owner_situation(
                property_data
            )
            
            # Market position
            features["market_position"] = self._analyze_market_position(
                property_data,
                market_data
            )
            
            return features
            
        except Exception as e:
            print(f"Error extracting features: {e}")
            return {}  # Return empty features on error
    
    def _mock_tax_status(self) -> float:
        """Generate mock tax status."""
        try:
            return np.random.choice(
                [0.0, 0.3, 0.7, 1.0],
                p=[0.7, 0.15, 0.1, 0.05]
            )
        except Exception as e:
            print(f"Error generating mock tax status: {e}")
            return 0.5  # Return default tax status on error
    
    def _get_foreclosure_status(self, property_data: Dict) -> float:
        """Analyze foreclosure status."""
        try:
            if "attom_data" in property_data:
                foreclosure = property_data["attom_data"].get(
                    "foreclosure",
                    {}
                )
                if foreclosure.get("status") == "active":
                    return 1.0
                elif foreclosure.get("status") == "pre":
                    return 0.7
                else:
                    return 0.0
            else:
                # Mock data - most properties not in foreclosure
                return np.random.choice(
                    [0.0, 0.7, 1.0],
                    p=[0.85, 0.1, 0.05]
                )
            
        except Exception as e:
            print(f"Error analyzing foreclosure status: {e}")
            return 0.5  # Return default foreclosure status on error
    
    def _analyze_vacancy(self, property_data: Dict) -> float:
        """Analyze vacancy indicators."""
        try:
            # Check ATTOM data first
            if "attom_data" in property_data:
                occupancy = property_data["attom_data"].get(
                    "occupancy",
                    {}
                )
                if occupancy.get("status") == "vacant":
                    return 1.0
                elif occupancy.get("status") == "unknown":
                    return 0.5
                else:
                    return 0.0
            else:
                # Mock vacancy data
                return np.random.choice(
                    [0.0, 0.5, 1.0],
                    p=[0.8, 0.15, 0.05]
                )
            
        except Exception as e:
            print(f"Error analyzing vacancy: {e}")
            return 0.5  # Return default vacancy status on error
    
    def _assess_maintenance(self, property_data: Dict) -> float:
        """Assess maintenance issues."""
        try:
            # Use real data if available
            if "attom_data" in property_data:
                building = property_data["attom_data"].get("building", {})
                condition = building.get("condition", "unknown")
                
                if condition == "poor":
                    return 1.0
                elif condition == "fair":
                    return 0.7
                elif condition == "good":
                    return 0.3
                else:
                    return 0.5
            else:
                # Mock maintenance score
                return np.random.choice(
                    [0.3, 0.5, 0.7, 1.0],
                    p=[0.4, 0.3, 0.2, 0.1]
                )
            
        except Exception as e:
            print(f"Error assessing maintenance: {e}")
            return 0.5  # Return default maintenance score on error
    
    def _analyze_owner_situation(self, property_data: Dict) -> float:
        """Analyze owner situation indicators."""
        try:
            # Use ATTOM data if available
            if "attom_data" in property_data:
                owner = property_data["attom_data"].get("owner", {})
                
                # Check for distress indicators
                indicators = []
                
                # Out of state owner
                if owner.get("is_out_of_state"):
                    indicators.append(0.3)
                
                # Length of ownership
                years_owned = owner.get("years_owned", 0)
                if years_owned > 20:
                    indicators.append(0.4)
                
                # Multiple properties
                if owner.get("other_properties", 0) > 3:
                    indicators.append(0.2)
                
                return max(indicators) if indicators else 0.5
            else:
                # Mock owner situation
                return np.random.choice(
                    [0.2, 0.4, 0.6, 0.8],
                    p=[0.4, 0.3, 0.2, 0.1]
                )
            
        except Exception as e:
            print(f"Error analyzing owner situation: {e}")
            return 0.5  # Return default owner situation score on error
    
    def _analyze_market_position(
        self,
        property_data: Dict,
        market_data: Optional[Dict]
    ) -> float:
        """Analyze property's market position."""
        try:
            if not market_data:
                return 0.5
            
            # Get property price
            price = property_data.get("price", 0)
            if not price:
                return 0.5
            
            # Compare to market metrics
            market_median = market_data.get("median_price", price)
            price_ratio = price / market_median
            
            # Score based on position
            if price_ratio <= 0.7:  # Significantly under market
                return 0.9
            elif price_ratio <= 0.8:
                return 0.7
            elif price_ratio <= 0.9:
                return 0.5
            else:
                return 0.3
            
        except Exception as e:
            print(f"Error analyzing market position: {e}")
            return 0.5  # Return default market position score on error
    
    def _calculate_distress_score(self, features: Dict) -> float:
        """Calculate overall distress score."""
        try:
            if not features:
                return 0.5  # Return default score for empty features
            
            # Calculate weighted score
            score = 0
            total_weight = 0
            
            for indicator, weight in self.indicators.items():
                if indicator in features:
                    score += features[indicator] * weight
                    total_weight += weight
            
            if total_weight == 0:
                return 0.5  # Return default score if no weights applied
            
            return score / total_weight
            
        except Exception as e:
            print(f"Error calculating distress score: {e}")
            return 0.5  # Return default score on error
    
    def _get_opportunity_level(self, score: float) -> str:
        """Get opportunity level based on distress score."""
        if score >= self.thresholds["high_potential"]:
            return "High Potential"
        elif score >= self.thresholds["medium_potential"]:
            return "Medium Potential"
        elif score >= self.thresholds["low_potential"]:
            return "Low Potential"
        else:
            return "Not Recommended"
    
    def _generate_recommendations(
        self,
        features: Dict,
        score: float
    ) -> List[str]:
        """Generate action recommendations."""
        recommendations = []
        
        # High distress score recommendations
        if score >= self.thresholds["high_potential"]:
            recommendations.append(
                "Immediate contact recommended - high distress indicators"
            )
            recommendations.append(
                "Prepare competitive cash offer"
            )
        
        # Specific feature recommendations
        if features.get("tax_delinquent", 0) > 0.7:
            recommendations.append(
                "Tax delinquency detected - research payment history"
            )
        
        if features.get("foreclosure_status", 0) > 0.5:
            recommendations.append(
                "Potential foreclosure situation - verify status"
            )
        
        if features.get("vacancy_status", 0) > 0.7:
            recommendations.append(
                "Property likely vacant - conduct drive-by inspection"
            )
        
        if features.get("maintenance_issues", 0) > 0.7:
            recommendations.append(
                "Significant maintenance issues - factor into offer"
            )
        
        if features.get("market_position", 0) > 0.7:
            recommendations.append(
                "Property significantly under market - verify condition"
            )
        
        return recommendations if recommendations else ["No specific recommendations"]
    
    def _calculate_confidence(
        self,
        property_data: Dict,
        features: Dict
    ) -> float:
        """Calculate confidence score for the analysis."""
        try:
            # Base confidence
            confidence = 0.6
            
            # Boost if we have ATTOM data
            if "attom_data" in property_data:
                confidence += 0.3
            
            # Adjust based on feature completeness
            feature_confidence = sum(
                1 for f in features.values()
                if f is not None
            ) / len(self.indicators)
            
            confidence *= feature_confidence
            
            # Cap at reasonable range
            return max(0.5, min(0.95, confidence))
            
        except Exception as e:
            print(f"Error calculating confidence score: {e}")
            return 0.5  # Return default confidence score on error
    
    def _get_default_analysis(self) -> Dict:
        """Get default analysis when errors occur."""
        return {
            "property_id": "",
            "distress_score": 0.5,
            "opportunity_level": "Unknown",
            "indicators": {},
            "recommendations": ["Unable to analyze property"],
            "confidence_score": 0.5
        }
