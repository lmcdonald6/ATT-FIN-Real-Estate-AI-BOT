#!/usr/bin/env python3
"""
Neighborhood Router

This module implements API routes for neighborhood sentiment analysis.
"""

import logging
from fastapi import APIRouter, Query, HTTPException

# Configure logging
logger = logging.getLogger(__name__)

# Import neighborhood analysis components
try:
    from src.neighborhood.neighborhood_full_pipeline import run_neighborhood_analysis
    logger.info("Successfully imported neighborhood analysis components")
except ImportError as e:
    logger.warning(f"Could not import neighborhood_full_pipeline: {e}. Using mock implementation.")
    # Mock implementation
    def run_neighborhood_analysis(zip_code):
        return {
            "score_report": {
                "score": 78.5,
                "summary": f"Neighborhood {zip_code} has a positive sentiment profile with strong community engagement."
            }
        }

# Create router
router = APIRouter(
    prefix="/sentiment",
    tags=["sentiment"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def get_sentiment(zip: str = Query(..., description="ZIP code to analyze")):
    """Get sentiment analysis for a neighborhood by ZIP code."""
    try:
        result = run_neighborhood_analysis(zip)
        return {
            "zip": zip,
            "score": result["score_report"].get("score"),
            "summary": result["score_report"].get("summary")
        }
    except Exception as e:
        logger.error(f"Error getting sentiment for ZIP {zip}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
