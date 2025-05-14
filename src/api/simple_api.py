#!/usr/bin/env python3
"""
Simple API Server for Real Estate Intelligence Core

This module implements a simplified FastAPI-based REST API for testing
the Real Estate Intelligence Core (REIC) functionality.
"""

import os
import sys
import json
import logging
from typing import Dict, Any, Optional
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
try:
    from fastapi import FastAPI, HTTPException, Query
    from fastapi.responses import JSONResponse, FileResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel
    logger.info("Successfully imported FastAPI components")
except ImportError as e:
    logger.error(f"Error importing FastAPI components: {e}")
    raise

# Import inference components
try:
    from src.inference.inference_layer_manager import InferenceLayerManager
    logger.info("Successfully imported inference components")
except ImportError as e:
    logger.error(f"Error importing inference components: {e}")
    raise

# Import export components
try:
    from src.utils.simple_export import simple_export
    logger.info("Successfully imported export components")
except ImportError as e:
    logger.error(f"Error importing export components: {e}")
    raise

# Create FastAPI app
app = FastAPI(
    title="Simple Real Estate Intelligence API",
    description="Simplified API for testing the Real Estate Intelligence Core",
    version="0.1.0"
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

# Store for analysis results
analysis_store = {}


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Simple Real Estate Intelligence API",
        "version": "0.1.0",
        "status": "active",
        "endpoints": [
            "/analyze",
            "/export/{format_type}"
        ]
    }


@app.get("/analyze")
async def analyze_query(
    query: str = Query(..., description="The natural language query to analyze"),
    zip_code: str = Query(..., description="The ZIP code to analyze")
):
    """Analyze a real estate query for a specific ZIP code."""
    try:
        # Create context with ZIP code
        context = {
            "zip_codes": [zip_code]
        }
        
        # Process the query using the inference manager
        result = inference_manager.process_query(query, context)
        
        # Generate a unique ID for this analysis
        analysis_id = f"analysis_{datetime.now().strftime('%Y%m%d%H%M%S')}_{hash(query) % 10000}"
        
        # Store the result
        analysis_store[analysis_id] = {
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "analysis": result
        }
        
        # Add the analysis ID to the result
        result["analysis_id"] = analysis_id
        
        return result
    except Exception as e:
        logger.error(f"Error analyzing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/export/{format_type}")
async def export_analysis(
    format_type: str,
    analysis_id: str = Query(..., description="ID of the analysis to export")
):
    """Export an analysis to the specified format."""
    try:
        # Validate format type
        valid_formats = ["pdf", "text", "csv", "json"]
        if format_type.lower() not in valid_formats:
            raise HTTPException(status_code=400, detail=f"Invalid format type. Must be one of: {', '.join(valid_formats)}")
        
        # Check if the analysis exists
        if analysis_id not in analysis_store:
            raise HTTPException(status_code=404, detail="Analysis not found")
        
        # Get the analysis
        analysis = analysis_store[analysis_id]
        
        # Extract ZIP code
        zip_code = "unknown"
        if "analysis" in analysis and "results" in analysis["analysis"]:
            zip_codes = list(analysis["analysis"]["results"].keys())
            if zip_codes:
                zip_code = zip_codes[0]
        
        # Prepare data for export
        export_data = {
            "zip": zip_code,
            "query": analysis.get("query", ""),
            "timestamp": datetime.now().isoformat(),
            "summary": "Analysis summary for " + zip_code
        }
        
        # Extract scores
        scores = {}
        if "analysis" in analysis and "results" in analysis["analysis"] and zip_code in analysis["analysis"]["results"]:
            result = analysis["analysis"]["results"][zip_code]
            for score_name in ["market_score", "reputation_score", "trend_score", "econ_score"]:
                if score_name in result:
                    scores[score_name.replace("_", " ").title()] = result.get(score_name, 0)
        
        # Add scores to export data
        export_data["scores"] = scores
        
        # Create output directory
        output_dir = os.path.join(sys_path, "output")
        os.makedirs(output_dir, exist_ok=True)
        
        # Export the analysis
        export_path = simple_export(export_data, format_type, output_dir)
        
        if not export_path or not os.path.exists(export_path):
            logger.error(f"Failed to generate export file")
            raise HTTPException(status_code=500, detail="Failed to generate export file")
        
        # Determine media type based on format
        if format_type.lower() == "pdf":
            media_type = "application/pdf"
            filename = f"real_estate_analysis_{zip_code}.pdf"
        elif format_type.lower() == "text":
            media_type = "text/plain"
            filename = f"real_estate_analysis_{zip_code}.txt"
        elif format_type.lower() == "csv":
            media_type = "text/csv"
            filename = f"real_estate_analysis_{zip_code}.csv"
        elif format_type.lower() == "json":
            media_type = "application/json"
            filename = f"real_estate_analysis_{zip_code}.json"
        else:
            media_type = "text/plain"
            filename = f"real_estate_analysis_{zip_code}.txt"
        
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


# Run the API server
def run_api_server():
    """Run the API server using uvicorn."""
    import uvicorn
    logger.info("Starting Simple Real Estate Intelligence API server...")
    logger.info("API documentation will be available at http://localhost:8000/docs")
    uvicorn.run("src.api.simple_api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    run_api_server()
