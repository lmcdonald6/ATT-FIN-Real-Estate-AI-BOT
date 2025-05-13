"""Market Economics Analysis Module

This module analyzes economic indicators including:
- Income requirements for homeownership
- Sales volume trends
- Inventory levels
- Market pressure indicators
"""

import os
from typing import Dict, Optional, Union, List
import pandas as pd
import numpy as np
from pydantic import BaseModel, Field
from dataclasses import dataclass
from datetime import datetime

@dataclass
class MarketMetrics:
    """Container for market metrics calculations"""
    affordability_ratio: float
    inventory_months: float
    sales_velocity: float
    price_to_income: float
    market_pressure: float

class EconomicsResult(BaseModel):
    """Market economics analysis result schema"""
    econ_score: Optional[float] = Field(None, ge=0, le=100)
    affordability_ratio: Optional[float] = None
    monthly_sales: Optional[int] = None
    inventory_level: Optional[int] = None
    price_to_income: Optional[float] = None
    market_health: str
    note: str
    warnings: List[str] = []

class MarketEconomicsAnalyzer:
    def __init__(self, data_dir: Optional[str] = None):
        """Initialize the market economics analyzer"""
        self.data_dir = data_dir or "data"
        self._load_data()

    def _load_data(self) -> None:
        """Load and validate economic indicator data"""
        try:
            # Load datasets
            self.income_df = pd.read_csv(os.path.join(self.data_dir, 
                "Metro_new_homeowner_income_needed_downpayment_0.20_uc_sfrcondo_tier_0.33_0.67_sm_sa_month.csv"))
            self.sales_df = pd.read_csv(os.path.join(self.data_dir,
                "Metro_sales_count_now_uc_sfrcondo_month.csv"))
            self.inv_df = pd.read_csv(os.path.join(self.data_dir,
                "Metro_invt_fs_uc_sfrcondo_sm_month.csv"))

            # Validate required columns
            for df, name in [(self.income_df, "income"), (self.sales_df, "sales"), (self.inv_df, "inventory")]:
                if "RegionName" not in df.columns:
                    raise ValueError(f"Missing RegionName column in {name} dataset")
                df["RegionName"] = df["RegionName"].str.lower()

        except FileNotFoundError as e:
            raise RuntimeError(f"Missing required data file: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Error loading market data: {str(e)}")

    def _calculate_metrics(self, region: str, actual_income: float) -> MarketMetrics:
        """Calculate key market metrics"""
        # Get latest data points
        income_needed = float(self.income_df[self.income_df["RegionName"] == region].iloc[0, -1])
        monthly_sales = float(self.sales_df[self.sales_df["RegionName"] == region].iloc[0, -1])
        inventory = float(self.inv_df[self.inv_df["RegionName"] == region].iloc[0, -1])

        # Calculate metrics
        affordability_ratio = income_needed / actual_income
        inventory_months = inventory / monthly_sales if monthly_sales > 0 else float('inf')
        sales_velocity = monthly_sales / inventory if inventory > 0 else 0
        price_to_income = income_needed / (actual_income * 0.28)  # 28% DTI ratio
        market_pressure = 1 / inventory_months if inventory_months > 0 else float('inf')

        return MarketMetrics(
            affordability_ratio=affordability_ratio,
            inventory_months=inventory_months,
            sales_velocity=sales_velocity,
            price_to_income=price_to_income,
            market_pressure=market_pressure
        )

    def get_market_score(self, region_name: str, actual_income: float = 80000) -> EconomicsResult:
        """
        Calculate market economics score based on affordability and market dynamics.
        
        Args:
            region_name: Name of the region to analyze
            actual_income: Actual household income (default: $80,000)
            
        Returns:
            EconomicsResult object containing:
            - econ_score: 0-100 score based on market health
            - affordability_ratio: Ratio of required to actual income
            - monthly_sales: Recent monthly sales volume
            - inventory_level: Current inventory level
            - price_to_income: Home price to income ratio
            - market_health: Overall market health assessment
            - note: Detailed market analysis
            - warnings: List of potential concerns
        """
        try:
            region = region_name.lower()
            warnings = []

            # Check if region exists in all datasets
            if not all(df["RegionName"].eq(region).any() for df in [self.income_df, self.sales_df, self.inv_df]):
                return EconomicsResult(
                    econ_score=None,
                    market_health="Unknown",
                    note=f"Region not found or incomplete data: {region_name}"
                )

            # Calculate metrics
            metrics = self._calculate_metrics(region, actual_income)

            # Base score calculation
            base_score = 70  # Start with neutral score

            # Affordability adjustments
            if metrics.affordability_ratio > 1.5:
                base_score -= 15
                warnings.append("Severe affordability concerns")
            elif metrics.affordability_ratio > 1.2:
                base_score -= 10
                warnings.append("Moderate affordability concerns")

            # Market pressure adjustments
            if metrics.inventory_months < 3:
                base_score += 10
                warnings.append("Low inventory levels")
            elif metrics.inventory_months > 6:
                base_score -= 10
                warnings.append("High inventory levels")

            # Sales velocity adjustments
            if metrics.sales_velocity > 0.33:  # Selling more than 1/3 of inventory monthly
                base_score += 5
            elif metrics.sales_velocity < 0.15:  # Selling less than 15% of inventory monthly
                base_score -= 5
                warnings.append("Slow sales velocity")

            # Determine market health
            if base_score >= 80:
                market_health = "Strong"
            elif base_score >= 65:
                market_health = "Healthy"
            elif base_score >= 50:
                market_health = "Stable"
            else:
                market_health = "Challenging"

            # Generate analysis note
            note = (
                f"Market shows {market_health.lower()} conditions with "
                f"{metrics.inventory_months:.1f} months of inventory. "
                f"Required income is {metrics.affordability_ratio:.1f}x "
                f"actual income. Monthly sales velocity: {metrics.sales_velocity:.2f}"
            )

            return EconomicsResult(
                econ_score=max(0, min(100, base_score)),
                affordability_ratio=round(metrics.affordability_ratio, 2),
                monthly_sales=int(self.sales_df[self.sales_df["RegionName"] == region].iloc[0, -1]),
                inventory_level=int(self.inv_df[self.inv_df["RegionName"] == region].iloc[0, -1]),
                price_to_income=round(metrics.price_to_income, 2),
                market_health=market_health,
                note=note,
                warnings=warnings
            )

        except Exception as e:
            return EconomicsResult(
                econ_score=None,
                market_health="Error",
                note=f"Error analyzing {region_name}: {str(e)}"
            )

# Create singleton instance
analyzer = MarketEconomicsAnalyzer()
