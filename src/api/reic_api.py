#!/usr/bin/env python3
"""
Real Estate Intelligence Core API

This module implements a FastAPI-based REST API for the
Real Estate Intelligence Core (REIC), providing endpoints for
natural language queries and report generation.
"""

import os
import sys
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)
    logger.info(f"Added {sys_path} to Python path")

# Import FastAPI components
from fastapi import FastAPI, Query, HTTPException, Depends
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# Import REIC components
from src.inference.inference_layer_manager import InferenceLayerManager
from src.utils.pdf_generator import generate_pdf_summary
from src.utils.simple_export import simple_export


# Define API models
class QueryRequest(BaseModel):
    """Model for natural language query requests."""
    prompt: str = Field(..., description="Natural language query about real estate")
    zip_code: str = Field(..., description="ZIP code to analyze")

class TrendRequest(BaseModel):
    """Model for market trend requests."""
    zip_code: str = Field(..., description="ZIP code to analyze")
    time_period: str = Field("5y", description="Time period for trend analysis (e.g., 1y, 5y, 10y)")

class SentimentRequest(BaseModel):
    """Model for sentiment analysis requests."""
    zip_code: str = Field(..., description="ZIP code to analyze")
    include_sources: bool = Field(False, description="Whether to include sentiment sources")

class ForecastRequest(BaseModel):
    """Model for market forecast requests."""
    zip_code: str = Field(..., description="ZIP code to analyze")
    forecast_period: str = Field("12m", description="Forecast period (e.g., 6m, 12m, 24m)")
    property_type: str = Field("residential", description="Property type (residential, commercial, etc.)")

class OpportunityRequest(BaseModel):
    """Model for investment opportunity discovery requests."""
    zip_code: str = Field(..., description="ZIP code to analyze")
    investment_horizon: str = Field("medium", description="Investment horizon (short, medium, long)")
    budget_range: str = Field("medium", description="Budget range (low, medium, high)")
    

class HealthResponse(BaseModel):
    """Model for health check response."""
    status: str
    timestamp: str
    version: str


# Create FastAPI app
app = FastAPI(
    title="Real Estate Intelligence API",
    description="API for the Real Estate Intelligence Core (REIC)",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize inference layer manager
inference_manager = InferenceLayerManager()


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "Real Estate Intelligence API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": [
            "/conversation/query",
            "/market/trends",
            "/sentiment/scores",
            "/market/forecasts",
            "/discovery/opportunities",
            "/export/pdf"
        ]
    }


@app.post("/conversation/query")
def conversation_query(req: QueryRequest):
    """Process a natural language query about real estate."""
    try:
        # Create context with ZIP code
        context = {
            "zip_codes": [req.zip_code]
        }
        
        # Process the query using the inference manager
        result = inference_manager.process_query(req.prompt, context)
        
        # Add metadata
        result["timestamp"] = datetime.now().isoformat()
        result["query"] = req.prompt
        result["zip_code"] = req.zip_code
        
        return result
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/market/trends")
def market_trends(req: TrendRequest):
    """Get historical market trends for a ZIP code."""
    try:
        # Create a specific query for the past layer
        query = f"What were the historical trends for ZIP code {req.zip_code} over the past {req.time_period}?"
        
        # Create context with ZIP code
        context = {
            "zip_codes": [req.zip_code],
            "time_period": req.time_period
        }
        
        # Process the query using the inference manager (will route to past layer)
        result = inference_manager.process_query(query, context)
        
        # Add metadata
        result["timestamp"] = datetime.now().isoformat()
        result["zip_code"] = req.zip_code
        result["time_period"] = req.time_period
        
        return result
    except Exception as e:
        logger.error(f"Error getting market trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/sentiment/scores")
def sentiment_scores(req: SentimentRequest):
    """Get current sentiment scores for a ZIP code."""
    try:
        # Create a specific query for the present layer
        query = f"What is the current sentiment for ZIP code {req.zip_code}?"
        
        # Create context with ZIP code and sources flag
        context = {
            "zip_codes": [req.zip_code],
            "include_sources": req.include_sources
        }
        
        # Process the query using the inference manager (will route to present layer)
        result = inference_manager.process_query(query, context)
        
        # Add metadata
        result["timestamp"] = datetime.now().isoformat()
        result["zip_code"] = req.zip_code
        
        return result
    except Exception as e:
        logger.error(f"Error getting sentiment scores: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/market/forecasts")
def market_forecasts(req: ForecastRequest):
    """Get market forecasts for a ZIP code."""
    try:
        # Create a specific query for the future layer
        query = f"What is the forecast for {req.property_type} real estate in ZIP code {req.zip_code} over the next {req.forecast_period}?"
        
        # Create context with ZIP code and forecast parameters
        context = {
            "zip_codes": [req.zip_code],
            "forecast_period": req.forecast_period,
            "property_type": req.property_type
        }
        
        # Process the query using the inference manager (will route to future layer)
        result = inference_manager.process_query(query, context)
        
        # Add metadata
        result["timestamp"] = datetime.now().isoformat()
        result["zip_code"] = req.zip_code
        result["forecast_period"] = req.forecast_period
        result["property_type"] = req.property_type
        
        return result
    except Exception as e:
        logger.error(f"Error getting market forecasts: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/discovery/opportunities")
def discovery_opportunities(req: OpportunityRequest):
    """Discover investment opportunities for a ZIP code."""
    try:
        # Create a specific query for multi-layer analysis
        query = f"Identify investment opportunities in ZIP code {req.zip_code} for {req.investment_horizon} term with {req.budget_range} budget."
        
        # Create context with ZIP code and opportunity parameters
        context = {
            "zip_codes": [req.zip_code],
            "investment_horizon": req.investment_horizon,
            "budget_range": req.budget_range
        }
        
        # Process the query using the inference manager (will use multiple layers)
        result = inference_manager.process_query(query, context)
        
        # Add metadata
        result["timestamp"] = datetime.now().isoformat()
        result["zip_code"] = req.zip_code
        result["investment_horizon"] = req.investment_horizon
        result["budget_range"] = req.budget_range
        
        return result
    except Exception as e:
        logger.error(f"Error discovering opportunities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/export/pdf")
def export_pdf(
    zip: str = Query(..., description="ZIP code to analyze"),
    summary: str = Query(..., description="Analysis summary"),
    market: float = Query(0.0, description="Market score"),
    rep: float = Query(0.0, description="Reputation score"),
    trend: float = Query(0.0, description="Trend score"),
    econ: float = Query(0.0, description="Economic score"),
    conf: float = Query(0.0, description="Investment confidence")
):
    """Generate and return a PDF summary report."""
    try:
        # Prepare scores dictionary
        scores = {
            "Market Score": market,
            "Reputation Score": rep,
            "Trend Score": trend,
            "Econ Score": econ,
            "Investment Confidence": conf
        }
        
        # Create output directory
        output_dir = os.path.join(sys_path, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate PDF
        pdf_path = generate_pdf_summary(zip, summary, scores, output_dir)
        
        if not pdf_path or not os.path.exists(pdf_path):
            logger.error("Failed to generate PDF")
            raise HTTPException(status_code=500, detail="Failed to generate PDF")
        
        # Return the PDF file
        return FileResponse(
            path=pdf_path,
            media_type="application/pdf",
            filename=os.path.basename(pdf_path)
        )
    except Exception as e:
        logger.error(f"Error generating PDF: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/export/{format_type}")
def export_analysis(
    format_type: str,
    zip: str = Query(..., description="ZIP code to analyze"),
    summary: str = Query(..., description="Analysis summary"),
    market: float = Query(0.0, description="Market score"),
    rep: float = Query(0.0, description="Reputation score"),
    trend: float = Query(0.0, description="Trend score"),
    econ: float = Query(0.0, description="Economic score"),
    conf: float = Query(0.0, description="Investment confidence")
):
    """Export analysis in the specified format (pdf, text, csv, json)."""
    try:
        # Validate format type
        valid_formats = ["pdf", "text", "csv", "json"]
        if format_type.lower() not in valid_formats:
            raise HTTPException(status_code=400, detail=f"Invalid format type. Must be one of: {', '.join(valid_formats)}")
        
        # Prepare export data
        export_data = {
            "zip": zip,
            "query": f"Real Estate Analysis for ZIP code {zip}",
            "timestamp": datetime.now().isoformat(),
            "summary": summary,
            "scores": {
                "Market Score": market,
                "Reputation Score": rep,
                "Trend Score": trend,
                "Econ Score": econ,
                "Investment Confidence": conf
            }
        }
        
        # Create output directory
        output_dir = os.path.join(sys_path, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Export the analysis
        export_path = simple_export(export_data, format_type.lower(), output_dir)
        
        if not export_path or not os.path.exists(export_path):
            logger.error("Failed to generate export file")
            raise HTTPException(status_code=500, detail="Failed to generate export file")
        
        # Determine media type based on format
        if format_type.lower() == "pdf":
            media_type = "application/pdf"
            filename = f"real_estate_analysis_{zip}.pdf"
        elif format_type.lower() == "text":
            media_type = "text/plain"
            filename = f"real_estate_analysis_{zip}.txt"
        elif format_type.lower() == "csv":
            media_type = "text/csv"
            filename = f"real_estate_analysis_{zip}.csv"
        elif format_type.lower() == "json":
            media_type = "application/json"
            filename = f"real_estate_analysis_{zip}.json"
        else:
            media_type = "text/plain"
            filename = f"real_estate_analysis_{zip}.txt"
        
        # Return the file
        return FileResponse(
            path=export_path,
            filename=filename,
            media_type=media_type
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error exporting analysis: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
def health():
    """Health check endpoint."""
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })
