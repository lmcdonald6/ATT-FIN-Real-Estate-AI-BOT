"""Market Analysis Integration Module

This module combines various market analysis components to provide
a comprehensive market assessment including:
- Market trends and appreciation
- Economic indicators
- Extended metrics
- Property-specific scores
- GPT-generated analysis
"""

import logging
from typing import Dict, Optional, Any
from dataclasses import dataclass
from pydantic import BaseModel, Field

from modules.market_trend import analyzer as trend_analyzer
from modules.market_economics import analyzer as econ_analyzer
from modules.extended_market_metrics import analyzer as ext_analyzer
from modules.property_score import combined_score
from modules.gpt_report import generate_property_report

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MarketAnalysisResult(BaseModel):
    """Complete market analysis result schema"""
    region: str
    final_score: Optional[float] = Field(None, ge=0, le=100)
    trend_score: Optional[float] = Field(None, ge=0, le=100)
    economic_score: Optional[float] = Field(None, ge=0, le=100)
    investment_score: Optional[float] = Field(None, ge=0, le=100)
    risk_level: str
    market_phase: str
    key_metrics: Dict[str, Any] = {}
    opportunities: list[str] = []
    risks: list[str] = []
    gpt_summary: Optional[str] = None
    error: Optional[str] = None

def analyze_market(
    region: str,
    rent: float,
    value: float,
    income: float = 80000
) -> MarketAnalysisResult:
    """
    Perform comprehensive market analysis combining multiple analysis components.
    
    Args:
        region: Name of the region to analyze
        rent: Monthly rental amount
        value: Property value
        income: Annual household income (default: $80,000)
        
    Returns:
        MarketAnalysisResult containing:
        - Combined analysis scores
        - Market trends
        - Economic indicators
        - Extended metrics
        - Risk assessment
        - GPT-generated summary
    """
    try:
        logger.info(f"Starting market analysis for {region}")
        
        # Get market trend analysis
        trend_result = trend_analyzer.get_trend_score(region)
        if not trend_result.trend_score:
            return MarketAnalysisResult(
                region=region,
                risk_level="Unknown",
                market_phase="Unknown",
                error=f"Failed to get trend data: {trend_result.note}"
            )

        # Get economic analysis
        econ_result = econ_analyzer.get_market_score(region, income)
        if not econ_result.econ_score:
            return MarketAnalysisResult(
                region=region,
                risk_level="Unknown",
                market_phase="Unknown",
                error=f"Failed to get economic data: {econ_result.note}"
            )

        # Get extended metrics
        ext_result = ext_analyzer.get_extended_metrics(region)
        if not ext_result.investment_score:
            return MarketAnalysisResult(
                region=region,
                risk_level="Unknown",
                market_phase="Unknown",
                error=f"Failed to get extended metrics: {ext_result.note}"
            )

        # Calculate property metrics
        monthly_payment = (value * 0.06) / 12  # Estimate monthly mortgage + expenses
        rental_yield = (rent * 12) / value
        rent_ratio = rent / monthly_payment
        
        # Score the property
        if rent_ratio > 1.2:
            rent_score = 85
            rent_note = "Strong rental potential"
        elif rent_ratio > 1.0:
            rent_score = 70
            rent_note = "Fair rental potential"
        else:
            rent_score = 55
            rent_note = "Below average rental potential"
        
        prop_result = {
            "rent_score": rent_score,
            "rent_note": rent_note,
            "rental_yield": rental_yield,
            "rent_ratio": rent_ratio
        }

        # Collect key metrics
        key_metrics = {
            "price_to_rent": ext_result.price_to_rent_ratio,
            "rental_yield": ext_result.rental_yield_pct,
            "appreciation_rate": trend_result.avg_appreciation * 100 if hasattr(trend_result, 'avg_appreciation') else None,
            "cost_of_living": ext_result.cost_of_living_index,
            "affordability_ratio": econ_result.affordability_ratio,
            "inventory_level": econ_result.inventory_level,
            "monthly_sales": econ_result.monthly_sales
        }

        # Combine opportunities and risks
        opportunities = ext_result.opportunities.copy()
        if trend_result.trend_score >= 75:
            opportunities.append("Strong price appreciation trend")
        if econ_result.econ_score >= 75:
            opportunities.append("Favorable economic conditions")

        risks = ext_result.concerns.copy()
        if trend_result.trend_score < 50:
            risks.append("Weak price appreciation")
        if econ_result.econ_score < 50:
            risks.append("Challenging economic conditions")

        # Calculate final investment score
        final_score = (
            trend_result.trend_score * 0.3 +
            econ_result.econ_score * 0.3 +
            ext_result.investment_score * 0.4
        )

        # Generate GPT summary
        try:
            analysis_data = {
                "zip": region,
                "rent_analysis": {
                    "score": prop_result["rent_score"],
                    "note": prop_result["rent_note"]
                },
                "appreciation_analysis": {
                    "score": trend_result.trend_score,
                    "note": trend_result.note
                },
                "risk_analysis": {
                    "vacancy_rate": econ_result.inventory_level / econ_result.monthly_sales if econ_result.monthly_sales else 0,
                    "tax_burden": key_metrics["cost_of_living"] / 100,
                    "score_penalty": len(risks) * 5
                },
                "final_score": final_score
            }
            gpt_result = generate_property_report(analysis_data)
            gpt_summary = gpt_result["report"] if gpt_result["success"] else None
        except Exception as e:
            logger.error(f"GPT report generation failed: {str(e)}")
            gpt_summary = None

        return MarketAnalysisResult(
            region=region,
            final_score=round(final_score, 1),
            trend_score=trend_result.trend_score,
            economic_score=econ_result.econ_score,
            investment_score=ext_result.investment_score,
            risk_level=ext_result.risk_level,
            market_phase=ext_result.market_phase,
            key_metrics=key_metrics,
            opportunities=opportunities,
            risks=risks,
            gpt_summary=gpt_summary
        )

    except Exception as e:
        logger.error(f"Market analysis failed: {str(e)}")
        return MarketAnalysisResult(
            region=region,
            risk_level="Error",
            market_phase="Unknown",
            error=f"Analysis failed: {str(e)}"
        )
