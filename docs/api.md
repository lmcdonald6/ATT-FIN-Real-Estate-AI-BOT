# API Documentation

## Overview

The Real Estate AI Analysis Platform provides a comprehensive REST API for property analysis, market insights, and investment recommendations. The API is secured with JWT authentication and includes rate limiting.

## Authentication

All API endpoints require authentication using either:
1. JWT token in Authorization header
2. API key in X-API-Key header

Example:
```bash
curl -H "Authorization: Bearer <token>" https://api.example.com/v1/properties
# or
curl -H "X-API-Key: <api_key>" https://api.example.com/v1/properties
```

## Rate Limiting

- Free tier: 100 requests/hour
- Pro tier: 1000 requests/hour
- Enterprise tier: Custom limits

## Endpoints

### Property Analysis

#### GET /v1/properties/analyze
Analyze a specific property using address and ZIP code.

```json
{
  "request": {
    "address": "123 Main St",
    "zipcode": "12345"
  },
  "response": {
    "property": {
      "details": {},
      "tax_data": {},
      "owner_info": {}
    },
    "market": {
      "trends": {},
      "predictions": {}
    },
    "neighborhood": {
      "score": 85,
      "schools": [],
      "amenities": [],
      "transportation": {}
    },
    "score": 0.75,
    "recommendation": "Consider investing"
  }
}
```

#### GET /v1/properties/search
Search for properties in a specific area.

```json
{
  "request": {
    "city": "San Francisco",
    "state": "CA",
    "zipcode": "94105",
    "filters": {
      "price_range": [500000, 1000000],
      "property_type": ["single_family", "condo"],
      "min_score": 0.7
    }
  },
  "response": {
    "properties": [
      {
        "address": "456 Market St",
        "details": {},
        "score": 0.85,
        "prediction": {}
      }
    ],
    "total": 10,
    "page": 1
  }
}
```

### Market Analysis

#### GET /v1/market/insights
Get market insights for a specific area.

```json
{
  "request": {
    "zipcode": "94105"
  },
  "response": {
    "current_market": {
      "median_price": 1200000,
      "inventory": 150,
      "days_on_market": 30
    },
    "predictions": {
      "price_trend": "increasing",
      "growth_rate": 0.05,
      "confidence": 0.85
    },
    "neighborhood": {
      "score": 80,
      "trends": {}
    }
  }
}
```

#### GET /v1/market/trends
Get historical and predicted market trends.

```json
{
  "request": {
    "zipcode": "94105",
    "timeframe": "1y"
  },
  "response": {
    "historical": [
      {
        "date": "2024-01",
        "median_price": 1150000
      }
    ],
    "predicted": [
      {
        "date": "2025-01",
        "median_price": 1250000,
        "confidence": 0.8
      }
    ]
  }
}
```

### Voice Interface

#### POST /v1/voice/query
Submit a voice query for natural language processing.

```json
{
  "request": {
    "audio": "base64_encoded_audio",
    "format": "wav"
  },
  "response": {
    "text": "Here's what I found about 123 Main St...",
    "data": {},
    "follow_up_questions": [
      "Would you like to know more about the neighborhood?"
    ]
  }
}
```

### Error Handling

All endpoints return standard HTTP status codes:
- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 429: Too Many Requests
- 500: Internal Server Error

Error response format:
```json
{
  "error": {
    "code": "RATE_LIMIT_EXCEEDED",
    "message": "Rate limit exceeded. Please try again later.",
    "details": {}
  }
}
```

## Webhooks

Subscribe to real-time updates:
- Property price changes
- Market trend alerts
- New listings
- Investment opportunities

```json
{
  "webhook_url": "https://your-server.com/webhook",
  "events": ["price_change", "new_listing"],
  "filters": {
    "zipcode": "94105",
    "min_price_change": 50000
  }
}
```

## SDKs

Official SDKs available for:
- Python
- JavaScript
- Java
- Ruby
- Go

Example Python usage:
```python
from wholesale import RealEstateAI

client = RealEstateAI(api_key="your_api_key")
analysis = await client.analyze_property("123 Main St", "12345")
print(analysis.score)
```
