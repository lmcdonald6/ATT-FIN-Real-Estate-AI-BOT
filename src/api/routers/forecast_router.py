#!/usr/bin/env python3
"""
Forecast Router

This module implements API routes for real estate market forecasts.
"""

import logging
from fastapi import APIRouter, Query, HTTPException

# Configure logging
logger = logging.getLogger(__name__)

# Import forecast components
try:
    from src.inference.future_layer import forecast_zip_trends
    logger.info("Successfully imported forecast components")
except ImportError as e:
    logger.warning(f"Could not import forecast_zip_trends: {e}. Using mock implementation.")
    # Mock implementation
    def forecast_zip_trends(zip_code):
        return {
            "price_trend": "upward",
            "confidence": 0.85,
            "forecast_period": "12m",
            "factors": [
                "Low inventory",
                "Strong economic indicators",
                "Increasing demand"
            ]
        }

# Create router
router = APIRouter(
    prefix="/forecast",
    tags=["forecast"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def get_forecast(zip: str = Query(..., description="ZIP code to forecast")):
    """Get market forecast for a ZIP code."""
    try:
        forecast = forecast_zip_trends(zip)
        return {
            "zip": zip,
            "forecast": forecast
        }
    except Exception as e:
        logger.error(f"Error getting forecast for ZIP {zip}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
