"""Extended Market Metrics Analysis Module

This module provides additional market analysis metrics including:
- Price-to-Rent ratios
- Cost of Living adjustments
- Construction activity impact
- Market saturation indicators
"""

import os
from typing import Dict, Optional, List, Union
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
from dataclasses import dataclass

@dataclass
class MarketIndicators:
    """Container for extended market indicators"""
    price_to_rent: float
    cost_of_living: float
    construction_activity: int
    rental_yield: float
    market_saturation: float

class ExtendedMetricsResult(BaseModel):
    """Extended market metrics result schema"""
    price_to_rent_ratio: Optional[float] = None
    rental_yield_pct: Optional[float] = None
    cost_of_living_index: Optional[float] = None
    active_permits: Optional[int] = None
    saturation_index: Optional[float] = None
    investment_score: Optional[float] = Field(None, ge=0, le=100)
    market_phase: str
    risk_level: str
    opportunities: List[str] = []
    concerns: List[str] = []
    note: str

class ExtendedMarketAnalyzer:
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the extended market analyzer"""
        self.data_dir = data_dir or "data"
        self._load_data()

    def _load_data(self) -> None:
        """Load and validate market data"""
        try:
            # Load home price data
            price_path = os.path.join(self.data_dir, "Metro_zhvi_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv")
            if not os.path.exists(price_path):
                raise FileNotFoundError(f"Price data file not found: {price_path}")
            
            self.price_df = pd.read_csv(price_path)
            self.price_df["RegionName"] = self.price_df["RegionName"].str.lower()

            # Load mock data (to be replaced with real data sources)
            self.rental_data = {
                "atlanta": {"rent": 1900, "trend": 0.05},
                "chicago": {"rent": 1800, "trend": 0.03},
                "los angeles": {"rent": 2900, "trend": 0.07}
            }

            self.col_data = {
                "atlanta": {"index": 96.5, "trend": "stable"},
                "chicago": {"index": 101.2, "trend": "rising"},
                "los angeles": {"index": 134.7, "trend": "rising"}
            }

            self.construction_data = {
                "atlanta": {"permits": 8, "yoy_change": 0.15},
                "chicago": {"permits": 4, "yoy_change": -0.05},
                "los angeles": {"permits": 12, "yoy_change": 0.25}
            }

        except Exception as e:
            raise RuntimeError(f"Failed to load market data: {str(e)}")

    def _calculate_indicators(self, region: str) -> MarketIndicators:
        """Calculate extended market indicators"""
        # Get latest price
        latest_price = float(self.price_df[self.price_df["RegionName"] == region].iloc[0, -1])
        
        # Get region data
        rental_info = self.rental_data.get(region, {"rent": 2000, "trend": 0})
        col_info = self.col_data.get(region, {"index": 100, "trend": "stable"})
        construction_info = self.construction_data.get(region, {"permits": 0, "yoy_change": 0})

        # Calculate metrics
        price_to_rent = latest_price / (rental_info["rent"] * 12)
        rental_yield = (rental_info["rent"] * 12) / latest_price
        
        return MarketIndicators(
            price_to_rent=price_to_rent,
            cost_of_living=col_info["index"],
            construction_activity=construction_info["permits"],
            rental_yield=rental_yield,
            market_saturation=construction_info["permits"] / 10  # Normalized to 0-1 scale
        )

    def get_extended_metrics(self, region_name: str) -> ExtendedMetricsResult:
        """
        Calculate extended market metrics for investment analysis.
        
        Args:
            region_name: Name of the region to analyze
            
        Returns:
            ExtendedMetricsResult object containing:
            - Various market ratios and indicators
            - Investment score
            - Market phase assessment
            - Risk level
            - Opportunities and concerns
            - Detailed analysis note
        """
        try:
            region = region_name.lower()
            
            # Check if region exists
            if not self.price_df["RegionName"].eq(region).any():
                return ExtendedMetricsResult(
                    market_phase="Unknown",
                    risk_level="Unknown",
                    note=f"Region not found: {region_name}"
                )

            # Calculate indicators
            indicators = self._calculate_indicators(region)
            
            # Initialize lists for analysis
            opportunities = []
            concerns = []
            
            # Analyze Price-to-Rent
            if indicators.price_to_rent < 15:
                opportunities.append("Favorable price-to-rent ratio")
                ptr_score = 85
            elif indicators.price_to_rent < 20:
                ptr_score = 70
            else:
                concerns.append("High price-to-rent ratio")
                ptr_score = 50

            # Analyze Cost of Living
            if indicators.cost_of_living <= 100:
                opportunities.append("Below average cost of living")
                col_score = 80
            elif indicators.cost_of_living <= 120:
                col_score = 65
            else:
                concerns.append("High cost of living")
                col_score = 50

            # Analyze Construction Activity
            if indicators.construction_activity > 10:
                concerns.append("Potential market saturation")
                construction_score = 60
            elif indicators.construction_activity > 5:
                construction_score = 75
            else:
                opportunities.append("Limited new supply")
                construction_score = 90

            # Calculate investment score
            investment_score = np.mean([ptr_score, col_score, construction_score])

            # Determine market phase
            if investment_score >= 80:
                market_phase = "Growth"
            elif investment_score >= 65:
                market_phase = "Stability"
            else:
                market_phase = "Caution"

            # Assess risk level
            if len(concerns) >= 2:
                risk_level = "High"
            elif len(concerns) == 1:
                risk_level = "Moderate"
            else:
                risk_level = "Low"

            # Generate analysis note
            note = (
                f"Market is in {market_phase.lower()} phase with {risk_level.lower()} risk. "
                f"Rental yield is {indicators.rental_yield*100:.1f}%. "
                f"Cost of living is {indicators.cost_of_living/100:.2f}x national average. "
                f"Construction activity: {indicators.construction_activity} active permits."
            )

            return ExtendedMetricsResult(
                price_to_rent_ratio=round(indicators.price_to_rent, 2),
                rental_yield_pct=round(indicators.rental_yield * 100, 1),
                cost_of_living_index=round(indicators.cost_of_living, 1),
                active_permits=indicators.construction_activity,
                saturation_index=round(indicators.market_saturation, 2),
                investment_score=round(investment_score, 1),
                market_phase=market_phase,
                risk_level=risk_level,
                opportunities=opportunities,
                concerns=concerns,
                note=note
            )

        except Exception as e:
            return ExtendedMetricsResult(
                market_phase="Error",
                risk_level="Unknown",
                note=f"Error analyzing {region_name}: {str(e)}"
            )

# Create singleton instance
analyzer = ExtendedMarketAnalyzer()
