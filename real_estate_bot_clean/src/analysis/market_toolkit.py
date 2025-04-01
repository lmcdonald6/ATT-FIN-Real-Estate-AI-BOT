"""
Enhanced market analysis toolkit integrating machine learning models
with our hybrid data approach (mock + ATTOM API).
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler
from datetime import datetime
from statsmodels.tsa.seasonal import seasonal_decompose

class MarketToolkit:
    def __init__(self):
        # Initialize ML model
        self.price_model = RandomForestRegressor(
            n_estimators=100,
            random_state=42
        )
        
        # Initialize with mock training data
        self._initialize_model()
        
        # Feature preprocessing
        self.scaler = StandardScaler()
        self.feature_columns = [
            'price', 'sqft', 'bedrooms', 'bathrooms',
            'year_built', 'days_on_market'
        ]
        
        # Market characteristics
        self.market_features = {
            "37215": {  # Belle Meade
                "market_strength": 0.85,
                "growth_rate": 0.12,
                "median_price": 1200000,
                "price_range": (800000, 3500000),
                "days_on_market": 45
            },
            "37203": {  # Downtown/Midtown
                "median_income": 85000,
                "population_density": 8500,
                "price_tier": "high",
                "growth_rate": 0.06,
                "market_strength": 0.80
            },
            # Atlanta Markets
            "30305": {  # Buckhead
                "median_income": 125000,
                "population_density": 4800,
                "price_tier": "luxury",
                "growth_rate": 0.07,
                "market_strength": 0.82
            },
            "30308": {  # Midtown
                "median_income": 75000,
                "population_density": 12000,
                "price_tier": "moderate",
                "growth_rate": 0.05,
                "market_strength": 0.75
            },
            # Dallas Markets
            "75225": {  # Highland Park
                "median_income": 150000,
                "population_density": 3800,
                "price_tier": "ultra-luxury",
                "growth_rate": 0.09,
                "market_strength": 0.90
            },
            "75201": {  # Downtown
                "median_income": 95000,
                "population_density": 11000,
                "price_tier": "high",
                "growth_rate": 0.06,
                "market_strength": 0.78
            }
        }
        
        # Seasonal patterns by ZIP
        self.seasonal_patterns = {
            "37215": {  # Belle Meade - luxury market
                "spring_boost": 0.08,  # Strong spring market
                "summer_boost": 0.05,  # Good summer activity
                "fall_boost": -0.02,   # Slight slowdown
                "winter_boost": -0.04,  # Holiday slowdown
                "peak_months": [3, 4, 5, 6],  # Mar-Jun
                "slow_months": [11, 12, 1]    # Nov-Jan
            },
            "37203": {  # Downtown/Midtown
                "spring_boost": 0.06,
                "summer_boost": 0.04,
                "fall_boost": -0.01,
                "winter_boost": -0.04,
                "peak_months": [3, 4, 5],  # March-May
                "slow_months": [11, 12, 1]  # Nov-Jan
            }
        }
        
        # Default seasonal pattern
        self.default_seasonal = {
            "spring_boost": 0.05,
            "summer_boost": 0.03,
            "fall_boost": -0.02,
            "winter_boost": -0.03,
            "peak_months": [4, 5, 6],
            "slow_months": [12, 1, 2]
        }
    
    def _initialize_model(self):
        """Initialize model with mock training data."""
        try:
            # Generate mock training data
            n_samples = 1000
            X = np.random.rand(n_samples, len(self.feature_columns))
            y = np.random.uniform(
                800000,
                3500000,
                size=n_samples
            )
            
            # Fit model
            self.price_model.fit(X, y)
            
        except Exception as e:
            print(f"Error initializing model: {e}")
    
    def _calculate_prediction_confidence(
        self,
        property_data: Dict,
        market_data: Dict
    ) -> float:
        """Calculate confidence score for prediction."""
        try:
            base_confidence = 0.6  # Base confidence
            
            # Boost if we have ATTOM data
            if "attom_data" in property_data:
                base_confidence += 0.2
            
            # Adjust based on data completeness
            required_fields = [
                'price', 'sqft', 'bedrooms',
                'bathrooms', 'year_built'
            ]
            completeness = sum(
                1 for f in required_fields
                if property_data.get(f) is not None
            ) / len(required_fields)
            
            confidence = base_confidence * completeness
            
            # Cap at reasonable range
            return max(0.5, min(0.95, confidence))
            
        except Exception as e:
            print(f"Error calculating confidence: {e}")
            return 0.5
    
    def analyze_market(
        self,
        zip_code: str,
        properties: List[Dict]
    ) -> Dict:
        """
        Comprehensive market analysis using both mock and enriched data.
        """
        try:
            if not properties:
                return self._get_default_analysis()
            
            # Get market features
            market = self.market_features.get(
                zip_code,
                self._get_default_market()
            )
            
            # Prepare data
            property_data = self._prepare_property_data(properties)
            
            # Calculate metrics
            price_metrics = self._calculate_price_metrics(property_data)
            market_metrics = self._calculate_market_metrics(
                property_data,
                market
            )
            trend_metrics = self._calculate_trend_metrics(
                property_data,
                market
            )
            
            # Add seasonal analysis
            seasonal = self.analyze_seasonality(zip_code, properties)
            
            # Update market analysis with seasonal factors
            market_metrics.update({
                "seasonal_analysis": seasonal,
                "current_market_phase": self._get_market_phase(
                    seasonal["current_season_impact"],
                    market_metrics["market_momentum"]
                )
            })
            
            return {
                "price_analysis": price_metrics,
                "market_analysis": market_metrics,
                "trend_analysis": trend_metrics,
                "opportunity_score": self._calculate_opportunity_score(
                    price_metrics,
                    market_metrics,
                    trend_metrics
                ),
                "analysis_date": datetime.now().isoformat()
            }
            
        except Exception as e:
            print(f"Error analyzing market: {e}")
            return self._get_default_analysis()
    
    def predict_property_values(
        self,
        properties: List[Dict],
        market_data: Dict
    ) -> List[Dict]:
        """
        Predict property values using ML model.
        Works with both mock and enriched data.
        Now includes seasonal adjustments.
        """
        try:
            if not properties:
                return []
            
            # Get current season impact
            current_month = datetime.now().month
            zip_code = properties[0].get("zip_code", "")
            patterns = self.seasonal_patterns.get(
                zip_code,
                self.default_seasonal
            )
            season_impact = self._calculate_season_impact(
                current_month,
                patterns
            )
            
            # Prepare features
            features = self._prepare_prediction_features(
                properties,
                market_data
            )
            
            if len(features) == 0:
                return []
            
            # Make predictions with seasonal adjustment
            predictions = []
            for i, prop in enumerate(properties):
                # Base prediction
                base_price = self.price_model.predict(
                    features[i].reshape(1, -1)
                )[0]
                
                # Apply seasonal adjustment
                adjusted_price = base_price * (1 + season_impact)
                
                # Calculate confidence
                confidence = self._calculate_prediction_confidence(
                    prop,
                    market_data
                )
                
                predictions.append({
                    "property_id": prop.get("id", ""),
                    "predicted_price": round(adjusted_price, -3),
                    "confidence_score": confidence,
                    "seasonal_adjustment": season_impact,
                    "seasonal_price_delta": round(
                        adjusted_price - base_price,
                        -3
                    ),
                    "prediction_date": datetime.now().isoformat()
                })
            
            return predictions
            
        except Exception as e:
            print(f"Error predicting values: {e}")
            return []
    
    def identify_opportunities(
        self,
        properties: List[Dict],
        market_data: Dict,
        min_score: float = 0.7
    ) -> List[Dict]:
        """
        Identify investment opportunities in the market.
        Uses both property data and market conditions.
        """
        try:
            opportunities = []
            
            for prop in properties:
                score = self._calculate_property_score(
                    prop,
                    market_data
                )
                
                if score >= min_score:
                    prop_data = prop.copy()
                    prop_data["opportunity_score"] = round(score * 100)
                    prop_data["recommendations"] = (
                        self._get_recommendations(prop, score)
                    )
                    opportunities.append(prop_data)
            
            # Sort by score
            opportunities.sort(
                key=lambda x: x["opportunity_score"],
                reverse=True
            )
            
            return opportunities
            
        except Exception as e:
            print(f"Error identifying opportunities: {e}")
            return []
    
    def _prepare_property_data(
        self,
        properties: List[Dict]
    ) -> pd.DataFrame:
        """Convert property list to DataFrame with feature engineering."""
        try:
            df = pd.DataFrame(properties)
            
            # Add derived features
            df["price_per_sqft"] = df["price"] / df["sqft"]
            df["age"] = 2024 - df["year_built"]
            
            # Encode property types
            type_map = {
                "Single Family": 3,
                "Townhouse": 2,
                "Condo": 1
            }
            df["property_type_code"] = df["property_type"].map(type_map)
            
            return df
            
        except Exception:
            return pd.DataFrame()
    
    def _calculate_price_metrics(self, df: pd.DataFrame) -> Dict:
        """Calculate price-related market metrics."""
        try:
            metrics = {
                "median_price": df["price"].median(),
                "avg_price": df["price"].mean(),
                "price_std": df["price"].std(),
                "median_ppsf": df["price_per_sqft"].median(),
                "avg_ppsf": df["price_per_sqft"].mean(),
                "ppsf_std": df["price_per_sqft"].std()
            }
            
            # Calculate price tiers
            metrics["price_tiers"] = {
                "low": df["price"].quantile(0.25),
                "mid": df["price"].quantile(0.5),
                "high": df["price"].quantile(0.75)
            }
            
            return metrics
            
        except Exception:
            return {}
    
    def _calculate_market_metrics(
        self,
        df: pd.DataFrame,
        market: Dict
    ) -> Dict:
        """Calculate general market condition metrics."""
        try:
            metrics = {
                "total_inventory": len(df),
                "avg_dom": df["days_on_market"].mean(),
                "median_dom": df["days_on_market"].median(),
                "inventory_by_type": df["property_type"].value_counts().to_dict(),
                "market_momentum": self._calculate_momentum(df, market)
            }
            
            # Add market characteristics
            metrics.update({
                "market_strength": market["market_strength"],
                "growth_rate": market["growth_rate"],
                "price_tier": market["price_tier"]
            })
            
            return metrics
            
        except Exception:
            return {}
    
    def _calculate_trend_metrics(
        self,
        df: pd.DataFrame,
        market: Dict
    ) -> Dict:
        """Calculate trend-related metrics."""
        try:
            # Sort by days on market
            df = df.sort_values("days_on_market")
            
            # Calculate 30-day metrics
            recent = df[df["days_on_market"] <= 30]
            older = df[df["days_on_market"] > 30]
            
            if len(recent) > 0 and len(older) > 0:
                price_trend = (
                    recent["price"].median() /
                    older["price"].median() - 1
                )
                dom_trend = (
                    recent["days_on_market"].median() /
                    older["days_on_market"].median() - 1
                )
            else:
                price_trend = 0
                dom_trend = 0
            
            return {
                "price_trend": price_trend,
                "dom_trend": dom_trend,
                "absorption_rate": len(recent) / len(df),
                "market_direction": self._get_market_direction(
                    price_trend,
                    dom_trend
                )
            }
            
        except Exception:
            return {}
    
    def _calculate_momentum(
        self,
        df: pd.DataFrame,
        market: Dict
    ) -> float:
        """Calculate market momentum score."""
        try:
            # Base momentum on recent activity
            recent = df[df["days_on_market"] <= 30]
            
            if len(recent) == 0:
                return 0.5
            
            # Factors
            inventory_factor = len(recent) / len(df)
            price_factor = recent["price"].median() / df["price"].median()
            
            # Calculate momentum
            momentum = (
                inventory_factor * 0.4 +
                price_factor * 0.4 +
                market["market_strength"] * 0.2
            )
            
            return max(0.0, min(1.0, momentum))
            
        except Exception:
            return 0.5
    
    def _calculate_opportunity_score(
        self,
        price_metrics: Dict,
        market_metrics: Dict,
        trend_metrics: Dict
    ) -> float:
        """Calculate overall market opportunity score."""
        try:
            # Weight the components
            weights = {
                "market_strength": 0.3,
                "growth_rate": 0.2,
                "momentum": 0.2,
                "absorption": 0.15,
                "price_trend": 0.15
            }
            
            score = (
                market_metrics["market_strength"] *
                weights["market_strength"] +
                market_metrics["growth_rate"] *
                weights["growth_rate"] +
                market_metrics["market_momentum"] *
                weights["momentum"] +
                trend_metrics["absorption_rate"] *
                weights["absorption"] +
                (1 + trend_metrics["price_trend"]) *
                weights["price_trend"]
            )
            
            return max(0.0, min(1.0, score))
            
        except Exception:
            return 0.5
    
    def _predict_single_property(
        self,
        property_data: Dict,
        features: np.ndarray,
        market_data: Dict
    ) -> Dict:
        """Make predictions for a single property."""
        try:
            # Base prediction
            base_price = self.price_model.predict(
                features.reshape(1, -1)
            )[0]
            
            # Adjust for market conditions
            adjusted_price = base_price * (
                1 + market_data.get("growth_rate", 0)
            )
            
            # Calculate confidence
            confidence = self._calculate_prediction_confidence(
                property_data,
                market_data
            )
            
            return {
                "property_id": property_data.get("id", ""),
                "predicted_price": round(adjusted_price, -3),
                "confidence_score": confidence,
                "prediction_date": datetime.now().isoformat()
            }
            
        except Exception:
            return {}
    
    def _get_market_direction(
        self,
        price_trend: float,
        dom_trend: float
    ) -> str:
        """Determine market direction from trends."""
        if price_trend > 0.02 and dom_trend < -0.05:
            return "Strong Seller's Market"
        elif price_trend > 0 and dom_trend < 0:
            return "Seller's Market"
        elif price_trend < -0.02 and dom_trend > 0.05:
            return "Strong Buyer's Market"
        elif price_trend < 0 and dom_trend > 0:
            return "Buyer's Market"
        else:
            return "Balanced Market"
    
    def _get_recommendations(
        self,
        property_data: Dict,
        score: float
    ) -> List[str]:
        """Generate recommendations based on property score."""
        recommendations = []
        
        if score >= 0.8:
            recommendations.append(
                "High-priority investment opportunity"
            )
            recommendations.append(
                "Consider ATTOM API enrichment for detailed analysis"
            )
        elif score >= 0.6:
            recommendations.append(
                "Potential investment opportunity"
            )
            recommendations.append(
                "Monitor market conditions"
            )
        else:
            recommendations.append(
                "Limited investment potential"
            )
            recommendations.append(
                "Consider alternative properties"
            )
        
        return recommendations
    
    def _get_default_market(self) -> Dict:
        """Get default market characteristics."""
        return {
            "median_income": 75000,
            "population_density": 5000,
            "price_tier": "moderate",
            "growth_rate": 0.05,
            "market_strength": 0.6
        }
    
    def _get_default_analysis(self) -> Dict:
        """Get default market analysis."""
        return {
            "price_analysis": {},
            "market_analysis": {},
            "trend_analysis": {},
            "opportunity_score": 0.5,
            "analysis_date": datetime.now().isoformat()
        }
    
    def analyze_seasonality(
        self,
        zip_code: str,
        historical_data: List[Dict]
    ) -> Dict:
        """
        Analyze seasonal patterns in the market.
        """
        try:
            if not historical_data:
                return self._get_default_seasonality()
            
            # Get seasonal patterns
            patterns = self.seasonal_patterns.get(
                zip_code,
                self.default_seasonal
            )
            
            # Calculate current season impact
            current_month = datetime.now().month
            season_impact = self._calculate_season_impact(
                current_month,
                patterns
            )
            
            # Only attempt seasonal decomposition with enough data
            seasonal_factors = {}
            if len(historical_data) >= 24:  # Need 2 years for decomposition
                df = pd.DataFrame(historical_data)
                df['date'] = pd.to_datetime(df['date'])
                df.set_index('date', inplace=True)
                
                monthly_avg = df.groupby(
                    df.index.month
                )['price'].mean()
                
                result = seasonal_decompose(
                    monthly_avg,
                    period=12,
                    extrapolate_trend=True
                )
                seasonal_factors = result.seasonal.to_dict()
            
            return {
                "current_season_impact": season_impact,
                "seasonal_factors": seasonal_factors,
                "peak_months": patterns["peak_months"],
                "slow_months": patterns["slow_months"],
                "price_adjustments": {
                    "spring": patterns["spring_boost"],
                    "summer": patterns["summer_boost"],
                    "fall": patterns["fall_boost"],
                    "winter": patterns["winter_boost"]
                }
            }
            
        except Exception as e:
            print(f"Error analyzing seasonality: {e}")
            return self._get_default_seasonality()
    
    def _calculate_season_impact(
        self,
        month: int,
        patterns: Dict
    ) -> float:
        """Calculate seasonal impact for current month."""
        # Spring (March-May)
        if month in [3, 4, 5]:
            return patterns["spring_boost"]
        # Summer (June-August)
        elif month in [6, 7, 8]:
            return patterns["summer_boost"]
        # Fall (September-November)
        elif month in [9, 10, 11]:
            return patterns["fall_boost"]
        # Winter (December-February)
        else:
            return patterns["winter_boost"]
    
    def _get_default_seasonality(self) -> Dict:
        """Get default seasonality analysis."""
        return {
            "current_season_impact": 0.0,
            "seasonal_factors": {},
            "peak_months": self.default_seasonal["peak_months"],
            "slow_months": self.default_seasonal["slow_months"],
            "price_adjustments": {
                "spring": self.default_seasonal["spring_boost"],
                "summer": self.default_seasonal["summer_boost"],
                "fall": self.default_seasonal["fall_boost"],
                "winter": self.default_seasonal["winter_boost"]
            }
        }
    
    def _get_market_phase(
        self,
        seasonal_impact: float,
        market_momentum: float
    ) -> str:
        """
        Determine current market phase using
        seasonal impact and momentum.
        """
        if seasonal_impact > 0.03 and market_momentum > 0.7:
            return "Strong Growth Phase"
        elif seasonal_impact > 0 and market_momentum > 0.5:
            return "Moderate Growth Phase"
        elif seasonal_impact < -0.03 and market_momentum < 0.3:
            return "Significant Slowdown"
        elif seasonal_impact < 0 and market_momentum < 0.5:
            return "Moderate Slowdown"
        else:
            return "Stable Phase"
    
    def _prepare_prediction_features(
        self,
        properties: List[Dict],
        market_data: Dict
    ) -> np.ndarray:
        """Prepare features for prediction model."""
        try:
            if not properties:
                return np.array([])
            
            # Convert to DataFrame
            df = pd.DataFrame(properties)
            
            # Extract features
            features = df[self.feature_columns].fillna(0)
            
            # Add market features
            features['market_strength'] = market_data.get(
                'market_strength',
                0.6
            )
            features['growth_rate'] = market_data.get(
                'growth_rate',
                0.05
            )
            
            # Scale features
            scaled = self.scaler.fit_transform(features)
            
            return scaled
            
        except Exception as e:
            print(f"Error preparing features: {e}")
            return np.array([])
    
    def _calculate_property_score(
        self,
        property_data: Dict,
        market_data: Dict
    ) -> float:
        """Calculate opportunity score for a property."""
        try:
            # Base score from market
            base_score = market_data.get("market_strength", 0.6)
            
            # Adjust for property characteristics
            price_factor = self._calculate_price_factor(
                property_data,
                market_data
            )
            location_factor = self._calculate_location_factor(
                property_data,
                market_data
            )
            
            # Calculate final score
            score = (
                base_score * 0.4 +
                price_factor * 0.3 +
                location_factor * 0.3
            )
            
            return max(0.0, min(1.0, score))
            
        except Exception as e:
            print(f"Error calculating property score: {e}")
            return 0.5
    
    def _calculate_price_factor(
        self,
        property_data: Dict,
        market_data: Dict
    ) -> float:
        """Calculate price-based factor for scoring."""
        try:
            price = property_data.get("price", 0)
            if not price:
                return 0.5
            
            # Get market metrics
            market_median = market_data.get("median_price", price)
            
            # Calculate price ratio
            price_ratio = price / market_median
            
            # Score based on ratio
            if price_ratio <= 0.8:
                return 0.9  # Good deal
            elif price_ratio <= 0.9:
                return 0.8
            elif price_ratio <= 1.1:
                return 0.7  # Fair price
            elif price_ratio <= 1.2:
                return 0.6
            else:
                return 0.5  # Expensive
            
        except Exception:
            return 0.5
    
    def _calculate_location_factor(
        self,
        property_data: Dict,
        market_data: Dict
    ) -> float:
        """Calculate location-based factor for scoring."""
        try:
            zip_code = property_data.get("zip_code", "")
            
            # Get market features
            market_features = self.market_features.get(
                zip_code,
                self._get_default_market()
            )
            
            # Calculate score based on market strength
            return market_features["market_strength"]
            
        except Exception:
            return 0.5
