#!/usr/bin/env python3
"""
Discovery Router

This module implements API routes for discovering investment opportunities.
"""

import logging
from fastapi import APIRouter, Query, HTTPException

# Configure logging
logger = logging.getLogger(__name__)

# Import discovery components
try:
    from src.discovery.opportunity_engine import discover_opportunity_zips
    logger.info("Successfully imported discovery components")
except ImportError as e:
    logger.warning(f"Could not import discover_opportunity_zips: {e}. Using mock implementation.")
    # Mock implementation
    def discover_opportunity_zips(limit=5):
        return [
            {"zip": "90210", "score": 92, "reason": "Strong price appreciation potential"},
            {"zip": "10001", "score": 88, "reason": "Emerging neighborhood with development plans"},
            {"zip": "60614", "score": 85, "reason": "High rental yield potential"},
            {"zip": "98101", "score": 82, "reason": "Tech industry growth driving demand"},
            {"zip": "78701", "score": 80, "reason": "Population growth exceeding housing supply"}
        ][:limit]

# Create router
router = APIRouter(
    prefix="/discover",
    tags=["discovery"],
    responses={404: {"description": "Not found"}},
)


@router.get("/")
def discover_zips(limit: int = Query(5, description="Number of opportunities to return")):
    """Discover top investment opportunity ZIP codes."""
    try:
        zips = discover_opportunity_zips(limit)
        return {
            "top_opportunities": zips
        }
    except Exception as e:
        logger.error(f"Error discovering opportunity ZIPs: {e}")
        raise HTTPException(status_code=500, detail=str(e))
