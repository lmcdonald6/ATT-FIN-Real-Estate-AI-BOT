#!/usr/bin/env python3
"""
API Routers Package

This package contains all the API routers for the Real Estate Intelligence Core.
"""

# Import all routers for easy access
from src.api.routers.neighborhood_router import router as neighborhood_router
from src.api.routers.forecast_router import router as forecast_router
from src.api.routers.discovery_router import router as discovery_router
