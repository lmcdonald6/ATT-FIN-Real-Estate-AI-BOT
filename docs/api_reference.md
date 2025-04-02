# API Reference

## Overview

The Real Estate AI System provides a comprehensive set of RESTful APIs for interacting with the system.

## Authentication

All API endpoints require authentication using JWT tokens.

```bash
curl -H "Authorization: Bearer <token>" https://api.example.com/v1/...
```

## API Endpoints

### Property Analysis

#### Get Property Analysis
```http
GET /api/v1/properties/{property_id}/analysis
```

Parameters:
- `property_id` (string): Property identifier

Response:
```json
{
    "property_id": "123",
    "valuation": {
        "estimated_price": 500000,
        "confidence": 0.85,
        "comparable_properties": [...]
    },
    "market_analysis": {
        "trend": "increasing",
        "risk_level": "low",
        "metrics": {...}
    },
    "investment_analysis": {
        "roi_potential": 0.12,
        "recommended_strategy": "buy_and_hold",
        "risk_factors": [...]
    }
}
```

#### Search Properties
```http
GET /api/v1/properties/search
```

Parameters:
- `location` (string): Location to search in
- `price_range` (object): Min and max price
- `property_type` (string): Type of property
- `features` (array): Required features

Response:
```json
{
    "results": [
        {
            "property_id": "123",
            "address": "...",
            "price": 500000,
            "features": {...},
            "analysis": {...}
        }
    ],
    "total": 100,
    "page": 1
}
```

### Market Analysis

#### Get Market Trends
```http
GET /api/v1/markets/{market_id}/trends
```

Parameters:
- `market_id` (string): Market identifier
- `timeframe` (string): Analysis timeframe

Response:
```json
{
    "market_id": "nyc_manhattan",
    "trends": {
        "price_trend": {
            "direction": "up",
            "strength": 0.7,
            "metrics": {...}
        },
        "inventory_trend": {...},
        "demand_trend": {...}
    },
    "opportunities": [...]
}
```

### Investment Analysis

#### Get Investment Recommendations
```http
POST /api/v1/investments/recommendations
```

Request:
```json
{
    "investment_type": "residential",
    "budget": {
        "min": 300000,
        "max": 700000
    },
    "strategy": "buy_and_hold",
    "risk_tolerance": "moderate"
}
```

Response:
```json
{
    "recommendations": [
        {
            "property_id": "123",
            "strategy": "buy_and_hold",
            "expected_roi": 0.15,
            "risk_level": "low",
            "analysis": {...}
        }
    ]
}
```

### Plugin Management

#### List Plugins
```http
GET /api/plugins
```

Response:
```json
{
    "plugins": [
        {
            "name": "zillow_data_source",
            "version": "1.0.0",
            "enabled": true,
            "capabilities": [...],
            "config": {...}
        }
    ]
}
```

#### Toggle Plugin
```http
POST /api/plugins/{plugin_name}/toggle
```

Response:
```json
{
    "status": "success",
    "enabled": true
}
```

#### Update Plugin Config
```http
POST /api/plugins/{plugin_name}/config
```

Request:
```json
{
    "config": {
        "setting1": "value1",
        "setting2": 42
    }
}
```

Response:
```json
{
    "status": "success"
}
```

### Data Integration

#### Fetch Property Data
```http
GET /api/v1/data/properties/{property_id}
```

Parameters:
- `property_id` (string): Property identifier
- `sources` (array): Data sources to query

Response:
```json
{
    "property_id": "123",
    "sources": {
        "zillow": {...},
        "mls": {...}
    },
    "consolidated": {...}
}
```

### Error Responses

All endpoints may return these errors:

#### 400 Bad Request
```json
{
    "error": "validation_error",
    "message": "Invalid parameter",
    "details": {...}
}
```

#### 401 Unauthorized
```json
{
    "error": "unauthorized",
    "message": "Invalid or expired token"
}
```

#### 403 Forbidden
```json
{
    "error": "forbidden",
    "message": "Insufficient permissions"
}
```

#### 404 Not Found
```json
{
    "error": "not_found",
    "message": "Resource not found"
}
```

#### 500 Internal Server Error
```json
{
    "error": "internal_error",
    "message": "An unexpected error occurred"
}
```

## Rate Limiting

API requests are limited to:
- 100 requests per minute per IP
- 1000 requests per hour per API key

Rate limit headers:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1623456789
```

## Webhooks

Subscribe to real-time updates:

```http
POST /api/v1/webhooks
```

Request:
```json
{
    "url": "https://your-server.com/webhook",
    "events": ["property.updated", "market.alert"],
    "secret": "your_webhook_secret"
}
```

Events:
- `property.updated`: Property data updates
- `market.alert`: Market condition alerts
- `analysis.completed`: Analysis completion
- `recommendation.available`: New recommendations

## SDKs and Libraries

Official SDKs:
- Python: `pip install wholesale-ai-client`
- JavaScript: `npm install wholesale-ai-client`
- Java: Available on Maven Central

## API Versioning

- Current version: v1
- Version in URL: `/api/v1/...`
- Deprecation notice: 6 months
- Sunset period: 12 months
