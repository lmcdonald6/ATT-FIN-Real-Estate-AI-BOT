"""Market Trend Analysis Module

This module analyzes historical price data to calculate market trends,
appreciation rates, and volatility scores for different regions.
"""

import os
from typing import Dict, Optional, Union
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field

class MarketTrendResult(BaseModel):
    """Market trend analysis result schema"""
    trend_score: Optional[float] = Field(None, ge=0, le=100)
    avg_appreciation: Optional[float] = None
    volatility: Optional[float] = None
    note: str
    raw_data: Optional[Dict] = None

class MarketTrendAnalyzer:
    def __init__(self, data_path: Optional[str] = None):
        """Initialize the market trend analyzer with data path"""
        self.data_path = data_path or os.path.join("data", "Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv")
        self._load_data()

    def _load_data(self) -> None:
        """Load and preprocess the market data"""
        try:
            if not os.path.exists(self.data_path):
                raise FileNotFoundError(f"Market data file not found: {self.data_path}")
            
            self.trend_df = pd.read_csv(self.data_path)
            
            # Validate required columns
            required_cols = ["RegionName"]
            missing_cols = [col for col in required_cols if col not in self.trend_df.columns]
            if missing_cols:
                raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")
            
            # Convert region names to lowercase for case-insensitive matching
            self.trend_df["RegionName"] = self.trend_df["RegionName"].str.lower()
            
        except Exception as e:
            raise RuntimeError(f"Failed to load market data: {str(e)}")

    def get_trend_score(self, region_name: str, months: int = 36) -> MarketTrendResult:
        """
        Calculate market trend score for a region based on historical price data.
        
        Args:
            region_name: Name of the region to analyze
            months: Number of months of historical data to analyze (default: 36)
            
        Returns:
            MarketTrendResult object containing:
            - trend_score: 0-100 score based on appreciation and volatility
            - avg_appreciation: Average monthly appreciation rate
            - volatility: Standard deviation of monthly changes
            - note: Descriptive analysis of the market trend
            - raw_data: Optional dictionary with raw calculation data
        """
        try:
            # Find region (case-insensitive)
            row = self.trend_df[self.trend_df["RegionName"] == region_name.lower()]
            if row.empty:
                return MarketTrendResult(
                    trend_score=None,
                    note=f"Region not found: {region_name}"
                )

            # Get price history (excluding metadata columns)
            price_series = row.iloc[0, 5:].dropna().astype(float).values[-months:]
            if len(price_series) < 12:
                return MarketTrendResult(
                    trend_score=None,
                    note=f"Insufficient data for {region_name}. Need at least 12 months."
                )

            # Calculate metrics
            pct_changes = np.diff(price_series) / price_series[:-1]
            avg_appreciation = float(np.mean(pct_changes))
            volatility = float(np.std(pct_changes))

            # Score calculation
            base_score = min(100, max(0, 50 + (avg_appreciation * 500) - (volatility * 300)))
            
            # Determine trend strength
            if avg_appreciation > 0.06 and volatility < 0.07:
                trend_score = min(100, base_score + 15)
                note = "Strong appreciation with low volatility"
            elif avg_appreciation > 0.04:
                trend_score = min(100, base_score + 5)
                note = "Stable growth with moderate volatility"
            elif avg_appreciation > 0.02:
                trend_score = base_score
                note = "Modest but consistent appreciation"
            elif avg_appreciation > 0:
                trend_score = max(0, base_score - 5)
                note = "Slow but positive appreciation"
            else:
                trend_score = max(0, base_score - 15)
                note = "Low or negative appreciation"

            # Add volatility context
            if volatility > 0.1:
                note += " (High price volatility)"
            elif volatility > 0.05:
                note += " (Moderate price volatility)"
            else:
                note += " (Stable prices)"

            return MarketTrendResult(
                trend_score=round(trend_score, 1),
                avg_appreciation=round(avg_appreciation, 4),
                volatility=round(volatility, 4),
                note=note,
                raw_data={
                    "price_history": price_series.tolist(),
                    "monthly_changes": pct_changes.tolist(),
                    "base_score": base_score
                }
            )

        except Exception as e:
            return MarketTrendResult(
                trend_score=None,
                note=f"Error analyzing {region_name}: {str(e)}"
            )

# Create singleton instance
analyzer = MarketTrendAnalyzer()
