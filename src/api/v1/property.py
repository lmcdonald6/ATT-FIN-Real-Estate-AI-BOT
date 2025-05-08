from fastapi import APIRouter, Depends, HTTPException, Query
from typing import Dict, List, Optional
from datetime import datetime

from ...services.property.service import PropertyService
from ...services.market.service import MarketAnalysisService
from ...models.property import PropertyDetails
from ...models.market import MarketAnalysis, TrendAnalysis
from ...utils.metrics import API_REQUEST_COUNT, API_LATENCY
from ...config import get_settings

router = APIRouter(prefix="/api/v1/properties", tags=["properties"])
settings = get_settings()

@router.get("/{property_id}", response_model=PropertyDetails, response_model_exclude_unset=True)
async def get_property_details(
    property_id: str,
    include_market: bool = Query(True, description="Include market analysis"),
    include_valuation: bool = Query(True, description="Include property valuation")
) -> PropertyDetails:
    """Get comprehensive property details including market analysis and valuation."""
    try:
        property_service = PropertyService(settings)
        details = await property_service.get_property_details(property_id)
        
        if include_market:
            market_service = MarketAnalysisService(settings)
            market_data = await market_service.analyze_market(details.location.zipcode)
            details.market_metrics = market_data.dict()
            
        return details
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{property_id}/analysis/investment", response_model=Dict)
async def analyze_investment_potential(
    property_id: str,
    forecast_months: int = Query(12, ge=1, le=60)
) -> Dict:
    """Analyze investment potential for a property."""
    try:
        property_service = PropertyService(settings)
        return await property_service.analyze_investment_potential(property_id)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{property_id}/analysis/market", response_model=MarketAnalysis)
async def get_market_analysis(
    property_id: str,
    timeframe: str = Query("1y", regex="^[0-9]+[ymwd]$")
) -> MarketAnalysis:
    """Get market analysis for the property's location."""
    try:
        property_service = PropertyService(settings)
        details = await property_service.get_property_details(property_id)
        
        market_service = MarketAnalysisService(settings)
        return await market_service.analyze_market(details.location.zipcode, timeframe)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{property_id}/analysis/trends", response_model=TrendAnalysis)
async def predict_market_trends(
    property_id: str,
    forecast_months: int = Query(12, ge=1, le=60)
) -> TrendAnalysis:
    """Predict market trends for the property's location."""
    try:
        property_service = PropertyService(settings)
        details = await property_service.get_property_details(property_id)
        
        market_service = MarketAnalysisService(settings)
        return await market_service.predict_trends(details.location.zipcode, forecast_months)
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))
