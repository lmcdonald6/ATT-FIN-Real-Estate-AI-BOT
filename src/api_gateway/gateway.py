"""API Gateway for the Real Estate Analysis System.

This module provides centralized authentication, rate limiting, and request routing
for the microservice architecture.
"""

import os
import jwt
import redis
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from ..utils.logging_config import get_logger

logger = get_logger(__name__)

class APIGateway:
    """
    API Gateway handling authentication, rate limiting, and request routing.
    
    Features:
    - JWT-based authentication
    - API key validation
    - Rate limiting
    - Usage tracking
    - Request routing
    """
    
    def __init__(self, config: Optional[Dict] = None):
        """
        Initialize the API Gateway.
        
        Args:
            config: Optional configuration dictionary with:
                - redis_host: Redis host (default: localhost)
                - redis_port: Redis port (default: 6379)
                - redis_db: Redis DB number (default: 0)
                - stripe_api_key: Stripe API key
                - jwt_secret: Secret for JWT encoding/decoding
                - api_rate_limit: Requests per window (default: 100)
                - api_rate_window: Window in seconds (default: 3600)
        """
        logger.info("Initializing API Gateway")
        self.config = config or {}
        
        # Initialize Redis client for rate limiting and caching
        self.redis_client = redis.Redis(
            host=self.config.get('redis_host', 'localhost'),
            port=self.config.get('redis_port', 6379),
            db=self.config.get('redis_db', 0)
        )
        
        # Only test connection if not in test mode
        if not self.config.get('testing', False):
            try:
                self.redis_client.ping()
                logger.info("Successfully connected to Redis")
            except redis.ConnectionError as e:
                logger.error(f"Failed to connect to Redis: {e}")
                raise
        
        # Initialize Stripe for payment processing
        try:
            import stripe
            stripe.api_key = self.config.get('stripe_api_key', os.getenv('STRIPE_API_KEY', ''))
        except ImportError:
            logger.warning("Stripe module not available")
            stripe = None
        
        # Set up FastAPI app
        self.app = FastAPI(title="Real Estate Analysis API")
        self.api_key_header = APIKeyHeader(name="X-API-Key")
        
        # Rate limiting configuration
        self.rate_limit = self.config.get('api_rate_limit', 100)
        self.rate_window = self.config.get('api_rate_window', 3600)
        
        # Register routes
        self._register_routes()
    
    def _register_routes(self):
        """Register API routes."""
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint."""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}
        
        @self.app.post("/auth/token")
        async def create_token(api_key: str = Depends(self.api_key_header)):
            """Create JWT token from API key."""
            if not self._validate_api_key(api_key):
                raise HTTPException(status_code=401, detail="Invalid API key")
            
            return {
                "access_token": self._create_jwt_token(api_key),
                "token_type": "bearer"
            }
    
    def _validate_api_key(self, api_key: str) -> bool:
        """
        Validate API key.
        
        Args:
            api_key: API key to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check if API key exists in Redis
            key_data = self.redis_client.hgetall(f"api_key:{api_key}")
            if not key_data:
                return False
            
            # Update last used timestamp
            self.redis_client.hset(
                f"api_key:{api_key}",
                "last_used",
                datetime.now().isoformat()
            )
            
            return True
        except redis.RedisError as e:
            logger.error(f"Error validating API key: {e}")
            return False
    
    def _create_jwt_token(self, api_key: str) -> str:
        """
        Create JWT token for API key.
        
        Args:
            api_key: API key to create token for
            
        Returns:
            str: JWT token
        """
        try:
            payload = {
                "sub": api_key,
                "exp": datetime.utcnow() + timedelta(days=1)
            }
            return jwt.encode(
                payload,
                self.config.get('jwt_secret', os.getenv('JWT_SECRET_KEY', '')),
                algorithm="HS256"
            )
        except Exception as e:
            logger.error(f"Error creating JWT token: {e}")
            raise HTTPException(
                status_code=500,
                detail="Could not create access token"
            )
    
    def _check_rate_limit(self, api_key: str) -> bool:
        """
        Check if request is within rate limit.
        
        Args:
            api_key: API key to check
            
        Returns:
            bool: True if within limit, False otherwise
        """
        try:
            key = f"rate_limit:{api_key}"
            current = self.redis_client.get(key)
            
            if current is None:
                # First request in window
                self.redis_client.setex(key, self.rate_window, 1)
                return True
            
            count = int(current)
            if count >= self.rate_limit:
                return False
            
            self.redis_client.incr(key)
            return True
        except redis.RedisError as e:
            logger.error(f"Error checking rate limit: {e}")
            return True  # Allow request on Redis error
    
    def track_usage(self, api_key: str, endpoint: str):
        """
        Track API usage for billing and monitoring.
        
        Args:
            api_key: API key of the request
            endpoint: Endpoint being accessed
        """
        try:
            now = datetime.now()
            day_key = now.strftime("%Y-%m-%d")
            
            # Increment daily counter
            self.redis_client.hincrby(
                f"usage:{api_key}:{day_key}",
                endpoint,
                1
            )
            
            # Set expiry for usage data (30 days)
            self.redis_client.expire(
                f"usage:{api_key}:{day_key}",
                60 * 60 * 24 * 30
            )
        except redis.RedisError as e:
            logger.error(f"Error tracking usage: {e}")
    
    def get_usage_stats(self, api_key: str) -> Dict[str, Any]:
        """
        Get usage statistics for an API key.
        
        Args:
            api_key: API key to get stats for
            
        Returns:
            Dict containing usage statistics
        """
        try:
            stats = {
                "total_requests": 0,
                "endpoints": {},
                "daily_usage": {}
            }
            
            # Get all usage keys for this API key
            usage_keys = self.redis_client.keys(f"usage:{api_key}:*")
            
            for key in usage_keys:
                day = key.decode().split(":")[-1]
                endpoint_stats = self.redis_client.hgetall(key)
                
                daily_total = 0
                for endpoint, count in endpoint_stats.items():
                    endpoint = endpoint.decode()
                    count = int(count)
                    daily_total += count
                    
                    # Update endpoint totals
                    stats["endpoints"][endpoint] = (
                        stats["endpoints"].get(endpoint, 0) + count
                    )
                
                stats["daily_usage"][day] = daily_total
                stats["total_requests"] += daily_total
            
            return stats
        except redis.RedisError as e:
            logger.error(f"Error getting usage stats: {e}")
            return {"error": str(e)}

# Create global instance if not in test mode
if not os.getenv('TESTING'):
    gateway = APIGateway()
else:
    gateway = None
