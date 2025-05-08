# Security Guide

## Overview

This guide covers security best practices and implementations for the Real Estate AI Analysis Platform.

## Authentication

### 1. JWT Implementation

```python
from datetime import datetime, timedelta
import jwt
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer

class JWTHandler:
    def __init__(self, secret_key: str):
        self.secret_key = secret_key
        self.algorithm = "HS256"
        self.security = HTTPBearer()
        
    def create_token(self, user_id: str, expires_delta: timedelta = None):
        """Create JWT token."""
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=1)
            
        payload = {
            "user_id": user_id,
            "exp": expire,
            "iat": datetime.utcnow()
        }
        
        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )
        
    async def verify_token(self, token: str = Security(HTTPBearer())):
        """Verify JWT token."""
        try:
            payload = jwt.decode(
                token.credentials,
                self.secret_key,
                algorithms=[self.algorithm]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=401,
                detail="Token has expired"
            )
        except jwt.JWTError:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )
```

### 2. API Key Management

```python
from typing import Optional
from pydantic import BaseModel
import hashlib
import secrets

class APIKey(BaseModel):
    key_id: str
    key_hash: str
    user_id: str
    expires_at: Optional[datetime]
    rate_limit: int = 1000
    
class APIKeyManager:
    def __init__(self, db_connection):
        self.db = db_connection
        
    def generate_key(self, user_id: str) -> str:
        """Generate new API key."""
        key = secrets.token_urlsafe(32)
        key_id = secrets.token_urlsafe(8)
        key_hash = self._hash_key(key)
        
        api_key = APIKey(
            key_id=key_id,
            key_hash=key_hash,
            user_id=user_id,
            expires_at=datetime.utcnow() + timedelta(days=365)
        )
        
        self.save_key(api_key)
        return f"{key_id}.{key}"
        
    def _hash_key(self, key: str) -> str:
        """Hash API key."""
        return hashlib.sha256(key.encode()).hexdigest()
        
    async def verify_key(self, key: str) -> bool:
        """Verify API key."""
        try:
            key_id, key_secret = key.split(".")
            stored_key = await self.get_key(key_id)
            
            if not stored_key:
                return False
                
            if stored_key.expires_at < datetime.utcnow():
                return False
                
            return self._hash_key(key_secret) == stored_key.key_hash
            
        except Exception:
            return False
```

## Rate Limiting

### 1. Redis-based Rate Limiter

```python
import redis
from fastapi import HTTPException

class RateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        
    async def check_rate_limit(
        self,
        key: str,
        limit: int,
        window: int = 3600
    ) -> bool:
        """Check if request is within rate limit."""
        pipe = self.redis.pipeline()
        
        # Get current count
        current = pipe.get(key)
        
        # Increment and set expiry
        pipe.incr(key)
        pipe.expire(key, window)
        
        results = pipe.execute()
        current = int(results[0] or 0)
        
        if current > limit:
            raise HTTPException(
                status_code=429,
                detail="Rate limit exceeded"
            )
            
        return True
        
    async def get_remaining(self, key: str, limit: int) -> int:
        """Get remaining requests."""
        current = int(self.redis.get(key) or 0)
        return max(0, limit - current)
```

### 2. IP-based Rate Limiting

```python
from fastapi import Request
from typing import Optional

class IPRateLimiter:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.window = 3600  # 1 hour
        self.limit = 1000   # requests per hour
        
    def get_client_ip(self, request: Request) -> str:
        """Get client IP from request."""
        forwarded = request.headers.get("X-Forwarded-For")
        if forwarded:
            return forwarded.split(",")[0]
        return request.client.host
        
    async def check_ip_rate_limit(
        self,
        request: Request,
        limit: Optional[int] = None
    ) -> bool:
        """Check IP-based rate limit."""
        ip = self.get_client_ip(request)
        key = f"rate_limit:ip:{ip}"
        return await self.check_rate_limit(
            key,
            limit or self.limit,
            self.window
        )
```

## Data Encryption

### 1. Data Encryption Service

```python
from cryptography.fernet import Fernet
from base64 import b64encode, b64decode

class EncryptionService:
    def __init__(self, key: bytes):
        self.fernet = Fernet(key)
        
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self.fernet.encrypt(
            data.encode()
        ).decode()
        
    def decrypt_data(self, encrypted: str) -> str:
        """Decrypt sensitive data."""
        return self.fernet.decrypt(
            encrypted.encode()
        ).decode()
        
    @staticmethod
    def generate_key() -> bytes:
        """Generate new encryption key."""
        return Fernet.generate_key()
```

### 2. Secure Configuration

```python
from typing import Dict
import yaml
from pathlib import Path

class SecureConfig:
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.encryption = EncryptionService(
            self._load_encryption_key()
        )
        
    def _load_encryption_key(self) -> bytes:
        """Load encryption key from environment."""
        key = os.environ.get("ENCRYPTION_KEY")
        if not key:
            raise ValueError("Missing encryption key")
        return b64decode(key)
        
    def load_config(self) -> Dict:
        """Load and decrypt configuration."""
        with open(self.config_path) as f:
            config = yaml.safe_load(f)
            
        # Decrypt sensitive values
        for key, value in config.items():
            if key.startswith("encrypted_"):
                plain_key = key[10:]  # Remove "encrypted_"
                config[plain_key] = self.encryption.decrypt_data(value)
                del config[key]
                
        return config
```

## Access Control

### 1. Role-Based Access Control

```python
from enum import Enum
from typing import List, Set

class Role(str, Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

class Permission(str, Enum):
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    ADMIN = "admin"

class RBAC:
    def __init__(self):
        self.role_permissions: Dict[Role, Set[Permission]] = {
            Role.ADMIN: {
                Permission.READ,
                Permission.WRITE,
                Permission.DELETE,
                Permission.ADMIN
            },
            Role.USER: {
                Permission.READ,
                Permission.WRITE
            },
            Role.READONLY: {
                Permission.READ
            }
        }
        
    def has_permission(
        self,
        role: Role,
        permission: Permission
    ) -> bool:
        """Check if role has permission."""
        return permission in self.role_permissions[role]
        
    def require_permission(
        self,
        role: Role,
        permission: Permission
    ):
        """Decorator to require permission."""
        def decorator(func):
            async def wrapper(*args, **kwargs):
                if not self.has_permission(role, permission):
                    raise HTTPException(
                        status_code=403,
                        detail="Permission denied"
                    )
                return await func(*args, **kwargs)
            return wrapper
        return decorator
```

### 2. Resource-Based Access Control

```python
from typing import List, Union

class Resource:
    def __init__(
        self,
        resource_id: str,
        owner_id: str,
        shared_with: List[str] = None
    ):
        self.resource_id = resource_id
        self.owner_id = owner_id
        self.shared_with = shared_with or []
        
class ResourceACL:
    def __init__(self, db_connection):
        self.db = db_connection
        
    async def check_access(
        self,
        user_id: str,
        resource: Resource,
        permission: Permission
    ) -> bool:
        """Check resource access."""
        # Owner has all permissions
        if resource.owner_id == user_id:
            return True
            
        # Check shared access
        if user_id in resource.shared_with:
            if permission == Permission.READ:
                return True
                
        return False
        
    async def grant_access(
        self,
        resource: Resource,
        user_id: str,
        permission: Permission
    ):
        """Grant resource access."""
        if permission == Permission.READ:
            resource.shared_with.append(user_id)
            await self.save_resource(resource)
```

## Security Headers

```python
from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next
    ) -> Response:
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = (
            "max-age=31536000; includeSubDomains"
        )
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
            "style-src 'self' 'unsafe-inline';"
        )
        
        return response
```

## Audit Logging

```python
import logging
from datetime import datetime
from typing import Dict, Any

class AuditLogger:
    def __init__(self):
        self.logger = logging.getLogger("audit")
        
    async def log_event(
        self,
        event_type: str,
        user_id: str,
        resource_id: str = None,
        details: Dict[str, Any] = None
    ):
        """Log security event."""
        event = {
            "timestamp": datetime.utcnow().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "resource_id": resource_id,
            "details": details or {},
            "ip_address": self.get_client_ip(),
            "user_agent": self.get_user_agent()
        }
        
        self.logger.info(
            "Security event",
            extra={"event": event}
        )
        
        # Store in database for compliance
        await self.store_event(event)
```

## Security Best Practices

1. **Authentication**
   - Use strong password policies
   - Implement MFA
   - Rotate tokens regularly
   - Lock accounts after failed attempts

2. **Authorization**
   - Follow principle of least privilege
   - Implement role-based access
   - Validate all permissions
   - Audit access regularly

3. **Data Protection**
   - Encrypt sensitive data
   - Use secure protocols
   - Implement backup strategies
   - Handle data deletion properly

4. **API Security**
   - Validate all inputs
   - Use rate limiting
   - Monitor for abuse
   - Version APIs properly

5. **Infrastructure**
   - Keep dependencies updated
   - Use security scanning
   - Monitor logs
   - Have incident response plan
