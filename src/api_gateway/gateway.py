from fastapi import FastAPI, Depends, HTTPException, Security
from fastapi.security import APIKeyHeader
from typing import Dict, Optional
from datetime import datetime, timedelta
import jwt
import redis
from pydantic import BaseModel
import stripe
from functools import wraps
import os

class APIGateway:
    def __init__(self):
        self.app = FastAPI(title="Real Estate AI Platform")
        self.redis_client = redis.Redis(host='localhost', port=6379, db=0)
        self.rate_limit_window = 3600  # 1 hour
        self.stripe = stripe.Stripe(os.getenv('STRIPE_SECRET_KEY'))
        
        # Initialize routes
        self.init_routes()
        
    def init_routes(self):
        @self.app.post("/api/v1/auth/token")
        async def get_token(api_key: str):
            """Generate JWT token for valid API keys"""
            if self.validate_api_key(api_key):
                return self.create_jwt_token(api_key)
            raise HTTPException(status_code=401, detail="Invalid API key")
            
        @self.app.get("/api/v1/usage/current")
        async def get_current_usage(token: str = Depends(self.validate_token)):
            """Get current API usage for the authenticated user"""
            user_id = self.get_user_from_token(token)
            return self.get_usage_stats(user_id)
            
    def rate_limit(self, calls_per_hour: int):
        """Rate limiting decorator"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                user_id = self.get_user_from_token(kwargs.get('token'))
                if not self.check_rate_limit(user_id, calls_per_hour):
                    raise HTTPException(status_code=429, detail="Rate limit exceeded")
                return await func(*args, **kwargs)
            return wrapper
        return decorator
        
    def validate_api_key(self, api_key: str) -> bool:
        """Validate API key against database"""
        # TODO: Implement actual validation against database
        return True
        
    def create_jwt_token(self, api_key: str) -> Dict:
        """Create JWT token for authentication"""
        expiration = datetime.utcnow() + timedelta(hours=24)
        data = {
            "sub": api_key,
            "exp": expiration
        }
        token = jwt.encode(data, os.getenv('JWT_SECRET_KEY'), algorithm="HS256")
        return {"access_token": token, "token_type": "bearer"}
        
    def check_rate_limit(self, user_id: str, limit: int) -> bool:
        """Check if user has exceeded their rate limit"""
        key = f"rate_limit:{user_id}"
        current = self.redis_client.get(key)
        if not current:
            self.redis_client.setex(key, self.rate_limit_window, 1)
            return True
        if int(current) >= limit:
            return False
        self.redis_client.incr(key)
        return True
        
    def track_usage(self, user_id: str, endpoint: str):
        """Track API usage for billing"""
        key = f"usage:{user_id}:{datetime.utcnow().strftime('%Y-%m-%d')}"
        self.redis_client.hincrby(key, endpoint, 1)
        
    def get_usage_stats(self, user_id: str) -> Dict:
        """Get usage statistics for a user"""
        today = datetime.utcnow().strftime('%Y-%m-%d')
        key = f"usage:{user_id}:{today}"
        return {
            "daily_usage": self.redis_client.hgetall(key),
            "rate_limit_remaining": self.get_remaining_calls(user_id)
        }
        
    def get_remaining_calls(self, user_id: str) -> int:
        """Get remaining API calls for the current window"""
        key = f"rate_limit:{user_id}"
        current = self.redis_client.get(key)
        return self.rate_limit_window - (int(current) if current else 0)

# Initialize the gateway
gateway = APIGateway()
app = gateway.app
