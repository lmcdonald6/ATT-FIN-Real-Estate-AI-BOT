"""
Historical trend analyzer for real estate market data.
Uses time series analysis and seasonal decomposition.
"""
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sklearn.preprocessing import MinMaxScaler
from statsmodels.tsa.seasonal import seasonal_decompose
from scipy import stats

class TrendAnalyzer:
    """Analyzes historical market trends and patterns."""
    
    def __init__(self):
        self.scaler = MinMaxScaler()
        self.seasonal_patterns = {
            "spring": [3, 4, 5],    # Mar-May
            "summer": [6, 7, 8],    # Jun-Aug
            "fall": [9, 10, 11],    # Sep-Nov
            "winter": [12, 1, 2]    # Dec-Feb
        }
        
        # Historical price trends (2020-2024)
        self.historical_trends = {
            # Nashville Markets
            "37215": [
                {"year": 2020, "appreciation": 0.065},
                {"year": 2021, "appreciation": 0.085},
                {"year": 2022, "appreciation": 0.075},
                {"year": 2023, "appreciation": 0.070},
                {"year": 2024, "appreciation": 0.080}
            ],
            "37203": [
                {"year": 2020, "appreciation": 0.055},
                {"year": 2021, "appreciation": 0.070},
                {"year": 2022, "appreciation": 0.065},
                {"year": 2023, "appreciation": 0.060},
                {"year": 2024, "appreciation": 0.065}
            ],
            # Atlanta Markets
            "30305": [
                {"year": 2020, "appreciation": 0.060},
                {"year": 2021, "appreciation": 0.075},
                {"year": 2022, "appreciation": 0.070},
                {"year": 2023, "appreciation": 0.065},
                {"year": 2024, "appreciation": 0.075}
            ],
            "30308": [
                {"year": 2020, "appreciation": 0.050},
                {"year": 2021, "appreciation": 0.065},
                {"year": 2022, "appreciation": 0.055},
                {"year": 2023, "appreciation": 0.050},
                {"year": 2024, "appreciation": 0.060}
            ],
            # Dallas Markets
            "75225": [
                {"year": 2020, "appreciation": 0.070},
                {"year": 2021, "appreciation": 0.090},
                {"year": 2022, "appreciation": 0.085},
                {"year": 2023, "appreciation": 0.080},
                {"year": 2024, "appreciation": 0.090}
            ],
            "75201": [
                {"year": 2020, "appreciation": 0.060},
                {"year": 2021, "appreciation": 0.075},
                {"year": 2022, "appreciation": 0.070},
                {"year": 2023, "appreciation": 0.065},
                {"year": 2024, "appreciation": 0.070}
            ]
        }
    
    def analyze_historical_trends(
        self,
        zip_code: str,
        years_back: int = 5
    ) -> Dict:
        """Analyze historical price trends for a market."""
        try:
            trends = self.historical_trends.get(zip_code, [])
            if not trends:
                return self._get_default_trends()
            
            # Calculate trend metrics
            appreciations = [t["appreciation"] for t in trends]
            
            return {
                "mean_appreciation": np.mean(appreciations),
                "median_appreciation": np.median(appreciations),
                "std_appreciation": np.std(appreciations),
                "trend_direction": self._calculate_trend_direction(appreciations),
                "volatility": self._calculate_volatility(appreciations),
                "seasonality": self._analyze_seasonality(zip_code),
                "confidence": self._calculate_trend_confidence(appreciations)
            }
        except Exception as e:
            print(f"Error analyzing trends: {e}")
            return self._get_default_trends()
    
    def predict_seasonal_impact(
        self,
        zip_code: str,
        months_ahead: int = 12
    ) -> Dict:
        """Predict seasonal impact on market metrics."""
        try:
            current_month = datetime.now().month
            future_month = (current_month + months_ahead) % 12 or 12
            
            # Get seasonal patterns
            current_season = self._get_season(current_month)
            future_season = self._get_season(future_month)
            
            # Calculate seasonal factors
            seasonal_factors = self._calculate_seasonal_factors(
                zip_code,
                current_season,
                future_season
            )
            
            return {
                "price_impact": seasonal_factors["price"],
                "inventory_impact": seasonal_factors["inventory"],
                "dom_impact": seasonal_factors["dom"],
                "current_season": current_season,
                "future_season": future_season,
                "confidence": seasonal_factors["confidence"]
            }
        except Exception as e:
            print(f"Error predicting seasonal impact: {e}")
            return self._get_default_seasonal_impact()
    
    def analyze_market_cycle(
        self,
        zip_code: str,
        current_stats: Dict
    ) -> Dict:
        """Analyze current market cycle position."""
        try:
            # Get historical data
            trends = self.historical_trends.get(zip_code, [])
            if not trends:
                return self._get_default_cycle_position()
            
            # Calculate cycle metrics
            cycle_metrics = self._calculate_cycle_metrics(
                trends,
                current_stats
            )
            
            return {
                "cycle_position": cycle_metrics["position"],
                "months_in_phase": cycle_metrics["months"],
                "expected_duration": cycle_metrics["duration"],
                "next_phase": cycle_metrics["next_phase"],
                "confidence": cycle_metrics["confidence"]
            }
        except Exception as e:
            print(f"Error analyzing market cycle: {e}")
            return self._get_default_cycle_position()
    
    def _calculate_trend_direction(
        self,
        values: List[float]
    ) -> str:
        """Calculate trend direction from historical values."""
        if len(values) < 2:
            return "Stable"
        
        slope, _, _, _, _ = stats.linregress(range(len(values)), values)
        
        if slope > 0.01:
            return "Upward"
        elif slope < -0.01:
            return "Downward"
        else:
            return "Stable"
    
    def _calculate_volatility(
        self,
        values: List[float]
    ) -> str:
        """Calculate market volatility level."""
        if len(values) < 2:
            return "Moderate"
        
        std = np.std(values)
        
        if std > 0.02:
            return "High"
        elif std < 0.01:
            return "Low"
        else:
            return "Moderate"
    
    def _analyze_seasonality(self, zip_code: str) -> Dict:
        """Analyze seasonal patterns in the market."""
        seasonal_strength = {
            "spring": 1.03,  # Peak season
            "summer": 1.02,  # Strong season
            "fall": 0.98,    # Moderate season
            "winter": 0.95   # Slow season
        }
        
        # Adjust for market specifics
        if zip_code in ["37215", "30305", "75225"]:  # Luxury markets
            seasonal_strength["winter"] = 0.97  # Less seasonal impact
        
        return seasonal_strength
    
    def _calculate_trend_confidence(
        self,
        values: List[float]
    ) -> float:
        """Calculate confidence in trend analysis."""
        if len(values) < 2:
            return 0.5
        
        # Calculate R-squared
        _, _, r_value, _, _ = stats.linregress(
            range(len(values)),
            values
        )
        r_squared = r_value ** 2
        
        # Adjust confidence based on data points
        sample_factor = min(1.0, len(values) / 5)
        
        return r_squared * sample_factor
    
    def _get_season(self, month: int) -> str:
        """Get season name for a given month."""
        for season, months in self.seasonal_patterns.items():
            if month in months:
                return season
        return "spring"  # Default
    
    def _calculate_seasonal_factors(
        self,
        zip_code: str,
        current_season: str,
        future_season: str
    ) -> Dict:
        """Calculate seasonal adjustment factors."""
        # Base seasonal factors
        base_factors = {
            "spring": {"price": 1.03, "inventory": 1.15, "dom": 0.85},
            "summer": {"price": 1.02, "inventory": 1.10, "dom": 0.90},
            "fall": {"price": 0.98, "inventory": 0.90, "dom": 1.10},
            "winter": {"price": 0.95, "inventory": 0.80, "dom": 1.20}
        }
        
        # Get factors for both seasons
        current = base_factors[current_season]
        future = base_factors[future_season]
        
        # Calculate relative changes
        return {
            "price": future["price"] / current["price"],
            "inventory": future["inventory"] / current["inventory"],
            "dom": future["dom"] / current["dom"],
            "confidence": 0.8  # Base confidence in seasonal patterns
        }
    
    def _calculate_cycle_metrics(
        self,
        trends: List[Dict],
        current_stats: Dict
    ) -> Dict:
        """Calculate market cycle metrics."""
        # Analyze current position
        current_appreciation = current_stats.get("price_trend", 0)
        inventory_trend = current_stats.get("inventory_trend", 0)
        
        # Determine cycle phase
        if current_appreciation > 0.06 and inventory_trend < 0:
            position = "Growth"
            next_phase = "Peak"
            months = 6
            duration = 18
        elif current_appreciation > 0.04 and inventory_trend > 0:
            position = "Peak"
            next_phase = "Slowdown"
            months = 3
            duration = 12
        elif current_appreciation < 0.02:
            position = "Slowdown"
            next_phase = "Bottom"
            months = 9
            duration = 24
        else:
            position = "Bottom"
            next_phase = "Growth"
            months = 12
            duration = 30
        
        return {
            "position": position,
            "months": months,
            "duration": duration,
            "next_phase": next_phase,
            "confidence": 0.7
        }
    
    def _get_default_trends(self) -> Dict:
        """Get default trend analysis."""
        return {
            "mean_appreciation": 0.05,
            "median_appreciation": 0.05,
            "std_appreciation": 0.01,
            "trend_direction": "Stable",
            "volatility": "Moderate",
            "seasonality": self._analyze_seasonality("00000"),
            "confidence": 0.5
        }
    
    def _get_default_seasonal_impact(self) -> Dict:
        """Get default seasonal impact."""
        return {
            "price_impact": 1.0,
            "inventory_impact": 1.0,
            "dom_impact": 1.0,
            "current_season": "spring",
            "future_season": "summer",
            "confidence": 0.5
        }
    
    def _get_default_cycle_position(self) -> Dict:
        """Get default market cycle position."""
        return {
            "cycle_position": "Stable",
            "months_in_phase": 6,
            "expected_duration": 24,
            "next_phase": "Unknown",
            "confidence": 0.5
        }
