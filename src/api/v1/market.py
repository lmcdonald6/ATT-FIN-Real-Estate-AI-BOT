from fastapi import APIRouter, HTTPException, Query
from typing import Dict, List, Optional
from datetime import datetime

from ...services.market.service import MarketAnalysisService
from ...models.market import MarketAnalysis, TrendAnalysis
from ...utils.metrics import API_REQUEST_COUNT, API_LATENCY
from ...config import get_settings

router = APIRouter(prefix="/api/v1/markets", tags=["markets"])
settings = get_settings()

@router.get("/{zipcode}/analysis", response_model=MarketAnalysis, response_model_exclude_unset=True)
async def get_market_analysis(
    zipcode: str,
    timeframe: str = Query("1y", regex="^[0-9]+[ymwd]$", description="Time frame for analysis (e.g., 1y, 6m, 30d)")
) -> MarketAnalysis:
    """Get comprehensive market analysis for a specific area."""
    try:
        market_service = MarketAnalysisService(settings)
        return await market_service.analyze_market(zipcode, timeframe)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{zipcode}/trends", response_model=TrendAnalysis, response_model_exclude_unset=True)
async def predict_market_trends(
    zipcode: str,
    forecast_months: int = Query(12, ge=1, le=60, description="Number of months to forecast"),
    include_opportunities: bool = Query(True, description="Include investment opportunities")
) -> TrendAnalysis:
    """Predict market trends and identify opportunities."""
    try:
        market_service = MarketAnalysisService(settings)
        return await market_service.predict_trends(zipcode, forecast_months)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/comparison", response_model=Dict[str, MarketAnalysis], response_model_exclude_unset=True)
async def compare_markets(
    zipcodes: List[str] = Query(..., min_items=2, max_items=5),
    timeframe: str = Query("1y", regex="^[0-9]+[ymwd]$")
) -> Dict[str, MarketAnalysis]:
    """Compare market analysis across multiple areas."""
    try:
        market_service = MarketAnalysisService(settings)
        results = {}
        
        for zipcode in zipcodes:
            results[zipcode] = await market_service.analyze_market(zipcode, timeframe)
            
        return results
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/opportunities", response_model=List[Dict], response_model_exclude_unset=True)
async def find_market_hotspots(
    state: str,
    min_roi: float = Query(5.0, ge=0, le=100, description="Minimum ROI percentage"),
    property_type: Optional[str] = Query(None, description="Filter by property type"),
    max_results: int = Query(10, ge=1, le=50)
) -> List[Dict]:
    """Find investment hotspots based on market analysis."""
    try:
        market_service = MarketAnalysisService(settings)
        # This will be implemented to scan multiple markets and find opportunities
        # For now, return a placeholder
        return []
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
