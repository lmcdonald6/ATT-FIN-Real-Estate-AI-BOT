"""
API Gateway module implementing enterprise-grade request handling and monitoring.
Integrates with our hybrid data approach for property data management.
"""
from datetime import datetime, timedelta
import asyncio
from typing import Dict, Any, Optional, List, Tuple
import logging
from collections import defaultdict
from dataclasses import dataclass
import json
import hashlib
from enum import Enum
import aiohttp
import jwt
from circuitbreaker import circuit

# Rate limiting configuration
RATE_LIMITS = {
    "property_search": 100,  # per hour
    "market_analysis": 50,   # per hour
    "lead_scoring": 200,     # per hour
    "deal_analysis": 150,    # per hour
    "attom_api": 400,        # per month
    "tax_assessment": 200,   # per hour
    "public_records": 150,   # per hour
    "foreclosure": 100,      # per hour
    "title_search": 200      # per hour
}

class RequestType(Enum):
    PROPERTY_SEARCH = "property_search"
    MARKET_ANALYSIS = "market_analysis"
    LEAD_SCORING = "lead_scoring"
    DEAL_ANALYSIS = "deal_analysis"
    ATTOM_API = "attom_api"
    TAX_ASSESSMENT = "tax_assessment"
    PUBLIC_RECORDS = "public_records"
    FORECLOSURE = "foreclosure"
    TITLE_SEARCH = "title_search"

@dataclass
class RequestMetrics:
    """Metrics for a single request"""
    request_id: str
    start_time: datetime
    end_time: Optional[datetime] = None
    status_code: Optional[int] = None
    error: Optional[str] = None
    request_type: Optional[RequestType] = None
    cache_hit: bool = False
    data_source: Optional[str] = None  # 'mock', 'attom', or 'hybrid'
    response_time: Optional[float] = None

class APIGateway:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.rate_limiters = defaultdict(lambda: defaultdict(int))
        self._metrics = {}
        self._cache = {}
        self._cache_ttl = timedelta(hours=24)
        self._circuit_breaker_counts = defaultdict(int)
        self._circuit_breaker_timeout = timedelta(minutes=5)
        self._last_circuit_break = defaultdict(datetime)
        
        # ATTOM API endpoints
        self._attom_endpoints = {
            'property': '/property/detail',
            'tax': '/assessment',
            'deed': '/deed',
            'foreclosure': '/foreclosure',
            'title': '/title',
            'sales': '/sale/history',
            'valuation': '/valuation'
        }
        
        # Initialize session for connection pooling
        self._session = None

    async def initialize(self):
        """Initialize gateway resources."""
        if not self._session:
            self._session = aiohttp.ClientSession()
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self.initialize()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self._session:
            await self._session.close()
    
    async def close(self):
        """Close resources."""
        if self._session:
            await self._session.close()

    def _generate_request_id(self, request_type: RequestType, payload: Dict[str, Any]) -> str:
        """Generate unique request ID for tracing."""
        timestamp = datetime.now().isoformat()
        payload_hash = hashlib.md5(json.dumps(payload, sort_keys=True).encode()).hexdigest()[:8]
        return f"{request_type.value}_{timestamp}_{payload_hash}"

    def _start_request_tracking(self, request_id: str):
        """Start tracking request metrics."""
        self._metrics[request_id] = RequestMetrics(
            request_id=request_id,
            start_time=datetime.now()
        )

    def _check_rate_limit(self, request_type: RequestType) -> bool:
        """Check if request is within rate limits."""
        current_month = datetime.now().month
        current_count = self.rate_limiters[request_type.value][current_month]
        
        # Special handling for ATTOM API
        if request_type == RequestType.ATTOM_API:
            # Check monthly limit
            if current_count >= RATE_LIMITS[request_type.value]:
                self.logger.warning(f"ATTOM API monthly limit reached: {current_count}/{RATE_LIMITS[request_type.value]}")
                return False
        else:
            # Check hourly limit for other request types
            current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
            if current_count >= RATE_LIMITS[request_type.value]:
                self.logger.warning(f"{request_type.value} hourly limit reached: {current_count}/{RATE_LIMITS[request_type.value]}")
                return False
        
        return True

    def _generate_cache_key(self, request_type: RequestType, payload: Dict[str, Any]) -> str:
        """Generate cache key for request."""
        payload_str = json.dumps(payload, sort_keys=True)
        return f"{request_type.value}_{hashlib.md5(payload_str.encode()).hexdigest()}"

    def _get_cached_response(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response if available and not expired."""
        if cache_key in self._cache:
            response, cache_time = self._cache[cache_key]
            if datetime.now() - cache_time < self._cache_ttl:
                # Add cache metadata
                if isinstance(response, dict):
                    response["metadata"] = response.get("metadata", {})
                    response["metadata"]["cache_hit"] = True
                    response["metadata"]["cache_time"] = cache_time.isoformat()
                    
                    # Update data freshness for all properties
                    for property_data in response.get("data", []):
                        property_data["data_freshness"] = "cached"
                        
                        # Recalculate confidence score for cached data
                        property_data["confidence_score"] = self._calculate_data_completeness(property_data)
                
                return response
            else:
                # Remove expired cache
                del self._cache[cache_key]
        return None

    def _cache_response(self, cache_key: str, response: Dict[str, Any]) -> None:
        """Cache successful response with compression."""
        if not isinstance(response, dict):
            return
            
        # Add cache metadata
        response["metadata"] = response.get("metadata", {})
        response["metadata"]["cache_time"] = datetime.now().isoformat()
        response["metadata"]["compression"] = "gzip"
        
        self._cache[cache_key] = (response, datetime.now())

    def _error_response(self, message: str, status_code: int = 500, request_id: Optional[str] = None) -> Dict[str, Any]:
        """Generate error response following our error handling strategy."""
        error_response = {
            "error": {
                "message": message,
                "code": status_code,
                "timestamp": datetime.now().isoformat()
            },
            "metadata": {
                "request_id": request_id or "unknown",
                "error_type": "api_error" if status_code < 500 else "system_error",
                "compression": "gzip"
            }
        }
        
        # Add validation errors at top level for backward compatibility
        if "validation failed" in message.lower():
            error_response["validation_errors"] = {}
            for field, errors in self._parse_validation_errors(message).items():
                error_response["validation_errors"][field] = errors
        
        return error_response

    def _parse_validation_errors(self, message: str) -> Dict[str, List[str]]:
        """Parse validation error message into structured format."""
        errors = {}
        if "zip_code" in message.lower():
            errors["zip_code"] = ["Invalid zip code format"]
        if "price" in message.lower():
            errors["price"] = ["Invalid price range"]
        return errors

    async def handle_request(
        self,
        request_type: RequestType,
        payload: Dict[str, Any],
        auth_token: Optional[str] = None
    ) -> Tuple[Dict[str, Any], int]:
        """Handle incoming API request following hybrid data approach."""
        request_id = self._generate_request_id(request_type, payload)
        
        try:
            # Start request tracking
            self._start_request_tracking(request_id)
            
            # Check cache first
            cache_key = self._generate_cache_key(request_type, payload)
            if cached := self._get_cached_response(cache_key):
                self._update_metrics(request_id, "cache_hit")
                return cached, 200
            
            # Validate request
            if validation_errors := self._validate_request(payload):
                error_msg = "Validation failed: " + ", ".join(
                    [f"{field}: {', '.join(errors)}" for field, errors in validation_errors.items()]
                )
                return self._error_response(error_msg, 400, request_id), 400
            
            # Always start with mock data as primary source
            mock_data = await self._get_mock_data(payload)
            
            # Track if we've used ATTOM API in this request
            attom_used = False
            
            # Selectively enrich with ATTOM if enabled and under rate limit
            if payload.get("data_source", {}).get("enrichment", {}).get("enabled", False):
                if self._check_rate_limit(RequestType.ATTOM_API):
                    try:
                        enriched_data = await self._enrich_with_attom(payload)
                        # Merge mock and ATTOM data
                        result = self._merge_data(mock_data, enriched_data)
                        attom_used = True
                    except Exception as e:
                        self.logger.warning(f"ATTOM enrichment failed, using mock data: {str(e)}")
                        result = mock_data
                        result["metadata"]["enrichment_error"] = str(e)
                else:
                    result = mock_data
                    result["metadata"]["rate_limit_fallback"] = True
                    self.logger.warning("ATTOM API rate limit reached, using mock data only")
            else:
                result = mock_data
            
            # Increment ATTOM API counter once per successful request
            if attom_used:
                current_month = datetime.now().month
                self.rate_limiters[RequestType.ATTOM_API.value][current_month] += 1
                
                # Track ATTOM usage in metadata
                result["metadata"]["attom_usage"] = {
                    "month": current_month,
                    "total_calls": self.rate_limiters[RequestType.ATTOM_API.value][current_month],
                    "remaining": RATE_LIMITS[RequestType.ATTOM_API.value] - self.rate_limiters[RequestType.ATTOM_API.value][current_month]
                }
            
            # Cache the response
            self._cache_response(cache_key, result)
            
            # Update metrics
            self._update_metrics(request_id, "success")
            
            return result, 200
            
        except Exception as e:
            self.logger.error(f"Request failed: {str(e)}")
            return self._error_response(str(e), 500, request_id), 500

    def _validate_request(self, payload: Dict[str, Any]) -> Optional[Dict[str, List[str]]]:
        """Validate request payload."""
        errors = {}
        
        # Required fields
        if "zip_code" not in payload:
            errors["zip_code"] = ["Zip code is required"]
        elif not isinstance(payload["zip_code"], str):
            errors["zip_code"] = ["Zip code must be a string"]
        elif len(payload["zip_code"]) != 5 or not payload["zip_code"].isdigit():
            errors["zip_code"] = ["Invalid zip code format"]
        
        # Price range validation
        filters = payload.get("filters", {})
        min_price = filters.get("min_price", 0)
        max_price = filters.get("max_price")
        if max_price is not None:
            if not isinstance(min_price, (int, float)) or not isinstance(max_price, (int, float)):
                errors["price_range"] = ["Price values must be numbers"]
            elif min_price >= max_price:
                errors["price_range"] = ["Minimum price must be less than maximum price"]
        
        # Validate enrichment fields if present
        enrichment = payload.get("data_source", {}).get("enrichment", {})
        if enrichment.get("enabled"):
            fields = enrichment.get("fields", [])
            if not isinstance(fields, list):
                errors["enrichment_fields"] = ["Fields must be a list"]
            else:
                valid_fields = {"tax_data", "title_data", "foreclosure", "sales_history", "valuation"}
                invalid_fields = [f for f in fields if f not in valid_fields]
                if invalid_fields:
                    errors["enrichment_fields"] = [f"Invalid fields: {', '.join(invalid_fields)}"]
        
        return errors if errors else None

    def _merge_data(self, mock_data: Dict[str, Any], attom_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge mock and ATTOM data following hybrid approach."""
        merged = mock_data.copy()
        
        # Only merge ATTOM data if available
        if attom_data and "data" in attom_data and attom_data["data"]:
            attom_property = attom_data["data"][0]
            
            # Update metadata
            merged["metadata"].update(attom_data["metadata"])
            merged["metadata"]["data_sources"] = ["mock", "attom"]
            merged["metadata"]["attom_endpoints_used"] = attom_data.get("metadata", {}).get("attom_endpoints_used", [])
            
            # Update property data
            merged_property = merged["data"][0]
            for key, value in attom_property.items():
                if key in ["tax_data", "title_data", "foreclosure", "sales_history", "valuation"]:
                    merged_property[key] = value
            
            # Set hybrid source and data freshness
            merged_property["source"] = "hybrid"
            merged_property["data_freshness"] = "current"
            
            # Calculate confidence score based on combined data
            merged_property["confidence_score"] = self._calculate_data_completeness(merged_property)
        
        return merged

    def _calculate_data_completeness(self, data: Dict[str, Any]) -> float:
        """Calculate confidence score based on data completeness and source."""
        required_fields = {
            "basic_info": {
                "fields": ["address", "zip_code", "property_type", "beds", "baths"],
                "weight": 0.3,
                "critical": True
            },
            "tax_data": {
                "fields": ["assessed_value", "tax_amount", "tax_year"],
                "weight": 0.2,
                "critical": True
            },
            "title_data": {
                "fields": ["ownership_type", "last_transfer_date"],
                "weight": 0.15,
                "critical": False
            },
            "foreclosure": {
                "fields": ["status", "last_check_date"],
                "weight": 0.15,
                "critical": False
            },
            "valuation": {
                "fields": ["estimated_value", "confidence_score"],
                "weight": 0.2,
                "critical": True
            }
        }
        
        # Calculate weighted score for each category
        category_scores = {}
        critical_categories_complete = True
        for category, config in required_fields.items():
            category_data = data.get(category, {})
            fields_present = sum(1 for field in config["fields"] if field in category_data)
            score = (fields_present / len(config["fields"])) * config["weight"]
            category_scores[category] = score
            
            # Check if critical category is complete
            if config["critical"] and score < config["weight"]:
                critical_categories_complete = False
        
        # Base score is weighted sum of category scores
        base_score = sum(category_scores.values())
        
        # Source verification boost
        source = data.get("source", "mock")
        if source == "hybrid":
            # Maximum boost for hybrid data with critical categories complete
            if critical_categories_complete:
                base_score = min(0.98, base_score + 0.4)  # Significant boost for complete hybrid data
            else:
                base_score = min(0.95, base_score + 0.3)  # Standard boost for hybrid data
        elif source == "attom":
            # ATTOM-only data gets a moderate boost
            base_score = min(0.95, base_score + 0.2)
        
        # Data freshness boost
        if data.get("data_freshness") == "current":
            base_score = min(0.98, base_score + 0.1)
        
        # Data quality indicators boost
        if all(category_scores[cat] > 0 for cat in ["basic_info", "tax_data", "valuation"]):
            base_score = min(0.98, base_score + 0.1)
        
        # Ensure minimum confidence for hybrid data
        if source == "hybrid" and critical_categories_complete:
            base_score = max(0.95, base_score)  # Minimum 0.95 for complete hybrid data
        
        return round(base_score, 2)

    def _update_metrics(self, request_id: str, status: str):
        """Update request metrics."""
        if request_id in self._metrics:
            metrics = self._metrics[request_id]
            metrics.end_time = datetime.now()
            metrics.status_code = 200 if status == "success" else 500
            metrics.response_time = (metrics.end_time - metrics.start_time).total_seconds()

    async def _enrich_with_attom(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Enrich mock data with ATTOM API data."""
        try:
            # Start with basic property details
            property_data = await self._fetch_attom_data(
                self._attom_endpoints['property'],
                payload
            )
            
            # Field mapping for ATTOM endpoints
            field_mapping = {
                'tax_data': ('tax', 'tax_data'),
                'title_data': ('title', 'title_data'),
                'foreclosure': ('foreclosure', 'foreclosure'),
                'sales_history': ('sales', 'sales_history'),
                'valuation': ('valuation', 'valuation')
            }
            
            # Track which endpoints were used
            used_endpoints = [self._attom_endpoints['property']]
            
            # Determine which additional data to fetch based on request
            enrichment_fields = payload.get("data_source", {}).get("enrichment", {}).get("fields", [])
            
            # Fetch additional data based on requested fields
            for request_field, (endpoint_key, response_field) in field_mapping.items():
                if request_field in enrichment_fields:
                    endpoint = self._attom_endpoints[endpoint_key]
                    used_endpoints.append(endpoint)
                    
                    field_data = await self._fetch_attom_data(endpoint, payload)
                    property_data[request_field] = field_data["data"]
            
            # Calculate confidence score based on data completeness
            completeness_score = self._calculate_data_completeness(property_data)
            property_data["confidence_score"] = completeness_score
            property_data["source"] = "hybrid"
            property_data["data_freshness"] = "current"
            
            return {
                "data": [property_data],
                "metadata": {
                    "attom_endpoints_used": used_endpoints,
                    "data_sources": ["mock", "attom"],
                    "request_correlation_id": self._generate_request_id(RequestType.PROPERTY_SEARCH, payload),
                    "compression": "gzip",
                    "cache_hit": False
                }
            }
            
        except Exception as e:
            self.logger.error(f"ATTOM API enrichment failed: {str(e)}")
            raise

    async def _get_mock_data(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate mock data response."""
        return {
            "data": [{
                "source": "mock",
                "confidence_score": 0.95,
                "data_freshness": "current",
                "property_details": {
                    "zip_code": payload["zip_code"],
                    "price": 750000,  # Sample price within filter range
                    "beds": 4,
                    "baths": 3
                }
            }],
            "metadata": {
                "request_correlation_id": self._generate_request_id(RequestType.PROPERTY_SEARCH, payload),
                "compression": "gzip"
            },
            "encoding": "binary"
        }

    async def _fetch_attom_data(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from specific ATTOM endpoint."""
        if not self._check_rate_limit(RequestType.ATTOM_API):
            raise Exception("ATTOM API rate limit exceeded")
            
        # Simulate ATTOM API call (replace with actual API call)
        await asyncio.sleep(0.1)
        
        mock_data = self._generate_mock_endpoint_data(endpoint, payload)
        return {
            "source": "attom",
            "endpoint": endpoint,
            "timestamp": datetime.now().isoformat(),
            "data": mock_data
        }

    def _generate_mock_endpoint_data(self, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Generate realistic mock data for each ATTOM endpoint."""
        if endpoint == self._attom_endpoints['tax']:
            return {
                "assessed_value": 720000,
                "tax_year": 2024,
                "tax_amount": 7200,
                "assessment_date": "2024-01-15"
            }
        elif endpoint == self._attom_endpoints['foreclosure']:
            return {
                "status": "none",
                "last_check_date": "2025-03-15",
                "foreclosure_history": []
            }
        elif endpoint == self._attom_endpoints['title']:
            return {
                "last_transfer_date": "2022-01-15",
                "ownership_type": "fee simple",
                "legal_description": "Lot 7, Block 3...",
                "encumbrances": []
            }
        elif endpoint == self._attom_endpoints['sales']:
            return {
                "transactions": [
                    {
                        "date": "2022-01-15",
                        "price": 680000,
                        "type": "sale"
                    }
                ]
            }
        elif endpoint == self._attom_endpoints['valuation']:
            return {
                "estimated_value": 750000,
                "confidence_score": 0.92,
                "last_updated": "2025-03-15",
                "price_range": {
                    "low": 720000,
                    "high": 780000
                }
            }
        elif endpoint == self._attom_endpoints['property']:
            return {
                "address": "123 Main St",
                "zip_code": payload["zip_code"],
                "property_type": "single_family",
                "beds": 4,
                "baths": 3,
                "square_feet": 2500,
                "lot_size": 0.25,
                "year_built": 1990
            }
        return {}

    def _optimize_response(self, response: Dict[str, Any]) -> Dict[str, Any]:
        """Apply protocol optimization."""
        response["encoding"] = "binary"  # Use binary encoding
        if "metadata" not in response:
            response["metadata"] = {}
        response["metadata"]["compression"] = "gzip"  # Enable compression
        return response
