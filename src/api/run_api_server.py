#!/usr/bin/env python3
"""
Run API Server

This script runs the FastAPI server for the Real Estate Intelligence API.
"""

import os
import sys
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)


def run_api_server():
    """Run the API server using uvicorn."""
    try:
        import uvicorn
        logger.info("Starting Real Estate Intelligence API server...")
        logger.info("API documentation will be available at http://localhost:8000/docs")
        uvicorn.run("src.api.intelligence_api:app", host="0.0.0.0", port=8000, reload=True)
    except ImportError:
        logger.error("uvicorn not installed. Please install it with 'pip install uvicorn'.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error starting API server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run_api_server()
