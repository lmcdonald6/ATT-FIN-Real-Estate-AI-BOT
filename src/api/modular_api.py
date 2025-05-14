#!/usr/bin/env python3
"""
Modular Real Estate Intelligence API

This module implements a modular FastAPI-based REST API for the
Real Estate Intelligence Core (REIC), using separate routers
for different functional areas.
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
from fastapi.openapi.docs import get_swagger_ui_html
from fastapi.staticfiles import StaticFiles

# Import routers
from src.api.routers.neighborhood_router import router as neighborhood_router
from src.api.routers.forecast_router import router as forecast_router
from src.api.routers.discovery_router import router as discovery_router

# Import export utilities
from src.utils.pdf_generator import generate_pdf_summary
from src.utils.simple_export import simple_export

# Create FastAPI app
app = FastAPI(
    title="Real Estate Intelligence API",
    description="Modular API for the Real Estate Intelligence Core (REIC)",
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

# Include routers
app.include_router(neighborhood_router, prefix="/api")
app.include_router(forecast_router, prefix="/api")
app.include_router(discovery_router, prefix="/api")


@app.get("/")
def root():
    """Root endpoint with API information."""
    return {
        "name": "Real Estate Intelligence API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": [
            "/api/sentiment",
            "/api/forecast",
            "/api/discover",
            "/export/pdf",
            "/health"
        ]
    }


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


@app.get("/health")
def health():
    """Health check endpoint."""
    return JSONResponse(content={
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    })
