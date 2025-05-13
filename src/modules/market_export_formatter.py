"""Market Analysis Export Formatter

This module formats market analysis results for export to various formats
(CSV, JSON, etc.) with consistent structure and proper error handling.
"""

from typing import Dict, Any, Optional, Union
from datetime import datetime
from pydantic import BaseModel, Field

class MarketExportData(BaseModel):
    """Schema for market analysis export data"""
    # Basic Information
    region: str
    status: str = "SUCCESS"
    timestamp: str = Field(default_factory=lambda: datetime.now().isoformat())
    error_message: Optional[str] = None

    # Core Metrics
    final_score: Optional[float] = None
    market_phase: Optional[str] = None
    risk_level: Optional[str] = None
    overall_recommendation: Optional[str] = None

    # Market Trends
    trend_score: Optional[float] = None
    appreciation_rate: Optional[float] = None
    price_volatility: Optional[float] = None
    historical_performance: Optional[str] = None

    # Economic Indicators
    economic_score: Optional[float] = None
    affordability_ratio: Optional[float] = None
    inventory_level: Optional[int] = None
    monthly_sales: Optional[int] = None
    market_velocity: Optional[float] = None

    # Extended Metrics
    price_to_rent_ratio: Optional[float] = None
    rental_yield: Optional[float] = None
    cost_of_living_index: Optional[float] = None
    construction_activity: Optional[int] = None
    market_saturation: Optional[float] = None

    # Risk Analysis
    risk_factors: list[str] = []
    opportunities: list[str] = []
    warning_flags: list[str] = []

    # Analysis Summary
    gpt_summary: Optional[str] = None
    analyst_notes: Optional[str] = None

def format_market_export(result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Format market analysis results for export.
    
    Args:
        result: Raw market analysis result dictionary
        
    Returns:
        Formatted dictionary ready for export to various formats
    """
    try:
        # Handle error cases
        if "error" in result:
            return MarketExportData(
                region=result.get("region", "Unknown"),
                status="ERROR",
                error_message=result["error"]
            ).dict(exclude_none=True)

        # Extract trend metrics
        trend_metrics = {
            "trend_score": result.get("trend_score"),
            "appreciation_rate": result.get("key_metrics", {}).get("appreciation_rate", 0) * 100 if result.get("key_metrics", {}).get("appreciation_rate") else None,
            "price_volatility": result.get("key_metrics", {}).get("volatility", 0) * 100 if result.get("key_metrics", {}).get("volatility") else None,
            "historical_performance": result.get("key_metrics", {}).get("trend_note")
        }

        # Extract economic indicators
        econ_metrics = {
            "economic_score": result.get("economic_score"),
            "affordability_ratio": result.get("key_metrics", {}).get("affordability_ratio"),
            "inventory_level": result.get("key_metrics", {}).get("inventory_level"),
            "monthly_sales": result.get("key_metrics", {}).get("monthly_sales")
        }

        # Calculate market velocity
        if econ_metrics["monthly_sales"] and econ_metrics["inventory_level"]:
            market_velocity = econ_metrics["monthly_sales"] / econ_metrics["inventory_level"]
        else:
            market_velocity = None

        # Extract extended metrics
        ext_data = result.get("extended", {})
        ext_metrics = {
            "price_to_rent_ratio": ext_data.get("price_to_rent_ratio"),
            "cost_of_living_index": ext_data.get("cost_of_living_index"),
            "construction_activity": ext_data.get("active_permits"),
            "market_saturation": ext_data.get("saturation_index")
        }

        # Calculate rental yield
        if ext_metrics["price_to_rent_ratio"]:
            rental_yield = (1 / ext_metrics["price_to_rent_ratio"]) * 100
        else:
            rental_yield = None

        # Determine overall recommendation
        if result.get("final_score", 0) >= 75:
            recommendation = "Strong Buy"
        elif result.get("final_score", 0) >= 65:
            recommendation = "Buy"
        elif result.get("final_score", 0) >= 50:
            recommendation = "Hold"
        else:
            recommendation = "Caution"

        # Format warning flags
        warning_flags = []
        if ext_metrics["price_to_rent_ratio"] and ext_metrics["price_to_rent_ratio"] > 20:
            warning_flags.append("High Price-to-Rent Ratio")
        if econ_metrics["affordability_ratio"] and econ_metrics["affordability_ratio"] > 1.2:
            warning_flags.append("Affordability Concerns")
        if market_velocity and market_velocity < 0.15:
            warning_flags.append("Slow Market Velocity")

        # Create export data
        export_data = MarketExportData(
            region=result["region"],
            final_score=result.get("final_score"),
            market_phase=result.get("market_phase"),
            risk_level=result.get("risk_level"),
            overall_recommendation=recommendation,
            
            # Market trends
            **trend_metrics,
            
            # Economic indicators
            **econ_metrics,
            market_velocity=market_velocity,
            
            # Extended metrics
            **ext_metrics,
            rental_yield=rental_yield,
            
            # Risk analysis
            risk_factors=result.get("risks", []),
            opportunities=result.get("opportunities", []),
            warning_flags=warning_flags,
            
            # Summary
            gpt_summary=result.get("summary", "")[:2000] if result.get("summary") else None,
            analyst_notes=f"Analysis performed on {datetime.now().strftime('%Y-%m-%d')}. "
                        f"Market shows {result.get('market_phase', '').lower()} conditions with "
                        f"{result.get('risk_level', '').lower()} risk profile."
        )

        return export_data.dict(exclude_none=True)

    except Exception as e:
        return MarketExportData(
            region=result.get("region", "Unknown"),
            status="ERROR",
            error_message=f"Export formatting failed: {str(e)}"
        ).dict(exclude_none=True)
