"""Financial Analysis API

This module provides a REST API for the financial analysis service.
"""

import os
import json
from typing import Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Body
from pydantic import BaseModel, Field
from dotenv import load_dotenv

# Import the analysis service
from financial_analysis_service.analysis_service import FinancialAnalysisService

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Real Estate Financial Analysis API",
    description="API for real estate financial analysis and investment insights",
    version="1.0.0"
)

# Initialize financial analysis service
analysis_service = FinancialAnalysisService()

# Define data models
class PropertyData(BaseModel):
    """Property data model for investment analysis."""
    address: str = Field(..., description="Property address")
    price: float = Field(..., description="Property price")
    property_type: Optional[str] = Field(None, description="Property type (e.g., single-family, multi-family, condo)")
    bedrooms: Optional[int] = Field(None, description="Number of bedrooms")
    bathrooms: Optional[float] = Field(None, description="Number of bathrooms")
    square_footage: Optional[int] = Field(None, description="Property square footage")
    year_built: Optional[int] = Field(None, description="Year property was built")
    lot_size: Optional[float] = Field(None, description="Lot size in acres")
    monthly_rent: float = Field(..., description="Monthly rental income")
    annual_income: Optional[float] = Field(None, description="Annual income from property")
    property_taxes: Optional[float] = Field(None, description="Annual property taxes")
    insurance: Optional[float] = Field(None, description="Annual insurance cost")
    maintenance: Optional[float] = Field(None, description="Annual maintenance cost")
    property_management: Optional[float] = Field(None, description="Annual property management cost")
    vacancy_rate: Optional[float] = Field(None, description="Vacancy rate percentage")
    appreciation_rate: Optional[float] = Field(None, description="Annual appreciation rate percentage")

class MarketData(BaseModel):
    """Market data model for market analysis."""
    region: str = Field(..., description="Market region or city")
    market_phase: str = Field(..., description="Current market phase (growth, peak, decline, recovery)")
    risk_level: Optional[str] = Field(None, description="Risk level (low, moderate, high, very high)")
    economic_score: Optional[float] = Field(None, description="Economic health score (0-100)")
    trend_score: Optional[float] = Field(None, description="Market trend score (0-100)")
    final_score: Optional[float] = Field(None, description="Overall market score (0-100)")
    ptr_ratio: Optional[float] = Field(None, description="Price-to-rent ratio")
    cap_rate: Optional[float] = Field(None, description="Capitalization rate percentage")
    monthly_sales: Optional[int] = Field(None, description="Monthly property sales volume")
    inventory_level: Optional[str] = Field(None, description="Inventory level (low, medium, high)")
    avg_appreciation: Optional[float] = Field(None, description="Average annual appreciation percentage")
    property_value: Optional[float] = Field(None, description="Average property value in the market")
    monthly_rent: Optional[float] = Field(None, description="Average monthly rent in the market")

class AnalysisResponse(BaseModel):
    """Response model for analysis endpoints."""
    status: str
    message: Optional[str] = None
    property: Optional[Dict[str, Any]] = None
    market: Optional[Dict[str, Any]] = None
    analysis: Optional[str] = None
    assessment: Optional[str] = None
    summary: Optional[str] = None

# API routes
@app.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Real Estate Financial Analysis API"}

@app.post("/analyze/investment", response_model=AnalysisResponse)
async def analyze_investment(property_data: PropertyData):
    """Analyze a real estate investment opportunity."""
    result = analysis_service.analyze_investment(property_data.dict(exclude_none=True))
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/analyze/risk", response_model=AnalysisResponse)
async def assess_risk(market_data: MarketData):
    """Assess the risk of a real estate market."""
    result = analysis_service.assess_risk(market_data.dict(exclude_none=True))
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/analyze/market-trends", response_model=AnalysisResponse)
async def analyze_market_trends(market_data: MarketData):
    """Analyze real estate market trends."""
    result = analysis_service.analyze_market_trends(market_data.dict(exclude_none=True))
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

@app.post("/generate/investment-summary", response_model=AnalysisResponse)
async def generate_investment_summary(property_data: PropertyData, market_data: MarketData):
    """Generate a comprehensive investment summary."""
    result = analysis_service.generate_investment_summary(
        property_data.dict(exclude_none=True),
        market_data.dict(exclude_none=True)
    )
    
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["message"])
    
    return result

# Run the API with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)
