"""API Gateway Service for Real Estate AI Bot.

This service provides a unified entry point for all microservices.
It handles routing, authentication, rate limiting, and request/response transformation.
"""

import os
import time
from typing import Dict, Any, Optional

from fastapi import FastAPI, Request, Response, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
import httpx
from pydantic import BaseModel

# Import logging configuration
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from src.utils.logging_config import setup_service_logging

# Setup service-specific logging
get_logger = setup_service_logging("api_gateway", "INFO")
logger = get_logger("main")

# Create FastAPI app
app = FastAPI(
    title="Real Estate AI Bot API Gateway",
    description="API Gateway for Real Estate AI Bot Microservices",
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

# API key security
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Define service endpoints
SERVICE_ENDPOINTS = {
    "financial_analysis": "http://financial_analysis:8001",
    "dashboard": "http://dashboard:8501",
    "data_scraping": "http://data_scraping:8000",
    "model_audit": "http://model_audit:8000",
    "ai_tools": "http://ai_tools:8000",
    "legacy": "http://app:8000"
}

# Rate limiting configuration
rate_limit_store = {}

# Models
class ErrorResponse(BaseModel):
    """Error response model."""
    status_code: int
    detail: str

class ServiceResponse(BaseModel):
    """Service response model."""
    service: str
    status: str
    data: Any

# Middleware
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """Add process time header to response."""
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

@app.middleware("http")
async def rate_limit_middleware(request: Request, call_next):
    """Rate limit middleware."""
    client_ip = request.client.host
    current_time = time.time()
    
    # Check if client is in rate limit store
    if client_ip in rate_limit_store:
        last_request_time, request_count = rate_limit_store[client_ip]
        
        # Reset count if more than 1 minute has passed
        if current_time - last_request_time > 60:
            rate_limit_store[client_ip] = (current_time, 1)
        else:
            # Increment count
            rate_limit_store[client_ip] = (last_request_time, request_count + 1)
            
            # Check if rate limit exceeded
            if request_count > 100:  # 100 requests per minute
                return JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={"detail": "Rate limit exceeded. Try again in a minute."}
                )
    else:
        # Add client to rate limit store
        rate_limit_store[client_ip] = (current_time, 1)
    
    return await call_next(request)

# Dependencies
async def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    """Verify API key."""
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="API key is missing"
        )
    
    # In production, validate against a secure store
    valid_api_keys = [os.getenv("API_GATEWAY_KEY", "test-api-key")]
    
    if api_key not in valid_api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key"
        )
    
    return api_key

# Routes
@app.get("/", include_in_schema=False)
async def root():
    """Root endpoint."""
    return {"message": "Real Estate AI Bot API Gateway"}

@app.get("/health")
async def health():
    """Health check endpoint."""
    return {"status": "healthy"}

@app.get("/services")
async def list_services(api_key: str = Depends(verify_api_key)):
    """List available services."""
    return {"services": list(SERVICE_ENDPOINTS.keys())}

@app.get("/services/{service_name}/health")
async def service_health(service_name: str, api_key: str = Depends(verify_api_key)):
    """Check health of a specific service."""
    if service_name not in SERVICE_ENDPOINTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_name}' not found"
        )
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SERVICE_ENDPOINTS[service_name]}/health",
                timeout=5.0
            )
            return {"service": service_name, "status": "healthy" if response.status_code == 200 else "unhealthy"}
    except Exception as e:
        logger.error(f"Error checking health of service {service_name}: {str(e)}")
        return {"service": service_name, "status": "unhealthy", "error": str(e)}

@app.api_route("/{service_name}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_request(
    service_name: str,
    path: str,
    request: Request,
    api_key: str = Depends(verify_api_key)
):
    """Proxy request to service."""
    if service_name not in SERVICE_ENDPOINTS:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Service '{service_name}' not found"
        )
    
    # Get target URL
    target_url = f"{SERVICE_ENDPOINTS[service_name]}/{path}"
    
    # Get request method and headers
    method = request.method
    headers = dict(request.headers)
    headers.pop("host", None)  # Remove host header
    
    # Get request body
    body = await request.body()
    
    # Log request
    logger.info(f"Proxying {method} request to {target_url}")
    
    try:
        # Send request to target service
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=target_url,
                headers=headers,
                content=body,
                timeout=30.0
            )
            
            # Return response
            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=dict(response.headers)
            )
    except httpx.RequestError as e:
        logger.error(f"Error proxying request to {target_url}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"Error communicating with service: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8080, reload=True)
