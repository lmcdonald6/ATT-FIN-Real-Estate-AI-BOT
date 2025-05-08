from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import time
from typing import Dict, Optional
import jwt
from datetime import datetime, timedelta

from ..config import get_settings
from ..utils.metrics import API_REQUEST_COUNT, API_LATENCY, GATEWAY_REQUEST_COUNT

logger = logging.getLogger(__name__)
settings = get_settings()

class APIGateway:
    def __init__(self):
        self.app = FastAPI(
            title="Real Estate AI Bot API Gateway",
            description="API Gateway for Real Estate Analysis Services",
            version="1.0.0"
        )
        self.setup_middleware()
        self.setup_routes()
        
    def setup_middleware(self):
        """Configure middleware for the gateway."""
        # CORS middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"]
        )
        
        # Request tracking middleware
        @self.app.middleware("http")
        async def track_requests(request: Request, call_next):
            start_time = time.time()
            
            # Track request metrics
            GATEWAY_REQUEST_COUNT.labels(
                path=request.url.path,
                method=request.method
            ).inc()
            
            # Process request
            try:
                response = await call_next(request)
                end_time = time.time()
                
                # Track latency
                API_LATENCY.labels(
                    endpoint=request.url.path
                ).observe(end_time - start_time)
                
                return response
            except Exception as e:
                logger.error(f"Gateway error: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Internal gateway error"}
                )
                
    def setup_routes(self):
        """Configure gateway routes."""
        @self.app.get("/health")
        async def health_check():
            return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
            
        @self.app.post("/auth/token")
        async def get_access_token(request: Request):
            """Generate JWT token for API access."""
            try:
                body = await request.json()
                api_key = body.get("api_key")
                
                if not self._validate_api_key(api_key):
                    return JSONResponse(
                        status_code=401,
                        content={"detail": "Invalid API key"}
                    )
                    
                token = self._generate_jwt_token(api_key)
                return {"access_token": token, "token_type": "bearer"}
            except Exception as e:
                logger.error(f"Token generation error: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={"detail": "Token generation failed"}
                )
                
    def _validate_api_key(self, api_key: str) -> bool:
        """Validate API key against configuration."""
        valid_keys = settings.get("api_keys", [])
        return api_key in valid_keys
        
    def _generate_jwt_token(self, api_key: str) -> str:
        """Generate JWT token for API authentication."""
        payload = {
            "sub": api_key,
            "exp": datetime.utcnow() + timedelta(days=1),
            "iat": datetime.utcnow()
        }
        return jwt.encode(
            payload,
            settings.jwt_secret_key,
            algorithm="HS256"
        )
        
    async def route_request(self, request: Request) -> Response:
        """Route incoming requests to appropriate services."""
        # Implement request routing logic here
        pass
        
gateway = APIGateway()
