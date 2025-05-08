from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from prometheus_client import make_asgi_app

from .api.v1 import property, market
from .utils.metrics import API_REQUEST_COUNT, API_LATENCY
from .config import get_settings, get_service_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize settings
settings = get_settings()
service_config = get_service_config()

# Create FastAPI app
app = FastAPI(
    title='Real Estate AI Bot',
    description='AI-powered real estate analysis and investment recommendations',
    version='1.0.0',
    docs_url='/docs',
    redoc_url='/redoc'
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configured in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add analyzer routes
app.include_router(analyzer_router)

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "timestamp": datetime.utcnow().isoformat(),
            "path": request.url.path
        }
    )

@app.get("/")
async def root():
    return {
        "name": "ATT-FIN Real Estate AI BOT",
        "version": "1.0.0",
        "status": "operational",
        "endpoints": {
            "analyzers": "/api/v1/analyze",
            "health": "/health",
            "docs": "/docs"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "components": {
            "api": "up",
            "database": "up",
            "cache": "up"
        },
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting ATT-FIN Real Estate AI BOT")
    uvicorn.run(app, host="0.0.0.0", port=8000)
