"""
Enhanced data manager implementing API Gateway patterns and gRPC optimization
for our hybrid data approach (mock + selective ATTOM API enrichment).
"""
from typing import Dict, List, Optional
import asyncio
import logging
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

@dataclass
class RequestMetrics:
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    last_request_time: Optional[datetime] = None

class DataManager:
    """
    Manages property data using hybrid approach:
    - Mock data as primary source (location-aware)
    - Selective ATTOM API enrichment (400 reports/month)
    - Smart caching (24h TTL)
    """
    
    def __init__(self):
        # API Gateway patterns
        self.rate_limiter = self._init_rate_limiter()
        self.circuit_breaker = self._init_circuit_breaker()
        self.cache = self._init_cache()
        self.metrics = RequestMetrics()
        
        # Logging setup
        self._setup_logging()
        
        # Track API usage
        self.api_calls = 0
        self.api_limit = 400  # Monthly limit
        
        # Property type distributions
        self.property_types = {
            "luxury": {
                "Single Family": 0.7,
                "Townhouse": 0.2,
                "Condo": 0.1
            },
            "high": {
                "Single Family": 0.5,
                "Townhouse": 0.3,
                "Condo": 0.2
            },
            "moderate": {
                "Single Family": 0.4,
                "Townhouse": 0.3,
                "Condo": 0.3
            }
        }
    
    def _init_rate_limiter(self) -> Dict:
        """Initialize rate limiter for ATTOM API."""
        return {
            "max_requests": 400,  # Monthly limit
            "time_window": timedelta(days=30),
            "current_requests": 0,
            "window_start": datetime.now()
        }
    
    def _init_circuit_breaker(self) -> Dict:
        """Initialize circuit breaker for API resilience."""
        return {
            "state": CircuitState.CLOSED,
            "failures": 0,
            "last_failure_time": None,
            "failure_threshold": 5,
            "reset_timeout": timedelta(minutes=15)
        }
    
    def _init_cache(self) -> Dict:
        """Initialize cache with TTL."""
        return {
            "data": {},
            "ttl": timedelta(hours=24)
        }
    
    def _setup_logging(self):
        """Configure logging for monitoring."""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    async def search_properties(
        self,
        zip_code: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search properties with enhanced error handling and circuit breaking.
        Implements API Gateway patterns for robust data handling.
        """
        try:
            # 1. Parameter validation
            if not self._validate_parameters(zip_code):
                raise ValueError("Invalid ZIP code format")
            
            # 2. Check rate limits
            if not self._check_rate_limit():
                self.logger.warning("Rate limit exceeded, using mock data")
                return await self._get_mock_data(zip_code, limit)
            
            # 3. Check circuit breaker
            if not self._check_circuit_breaker():
                self.logger.warning("Circuit breaker open, using mock data")
                return await self._get_mock_data(zip_code, limit)
            
            # 4. Check cache
            cached_data = self._get_from_cache(f"properties_{zip_code}")
            if cached_data:
                self.logger.info("Cache hit for ZIP: %s", zip_code)
                return cached_data[:limit]
            
            # 5. Attempt ATTOM API call
            try:
                properties = await self._fetch_from_attom(zip_code)
                self._record_success()
                self._update_cache(f"properties_{zip_code}", properties)
                return properties[:limit]
            except Exception as e:
                self._record_failure()
                self.logger.error("ATTOM API error: %s", str(e))
                return await self._get_mock_data(zip_code, limit)
            
        except Exception as e:
            self.logger.error("Property search error: %s", str(e))
            return await self._get_mock_data(zip_code, limit)
        finally:
            self._update_metrics()
    
    def _validate_parameters(self, zip_code: str) -> bool:
        """Validate input parameters."""
        return bool(zip_code and len(zip_code) == 5 and zip_code.isdigit())
    
    def _check_rate_limit(self) -> bool:
        """Check if within rate limits."""
        now = datetime.now()
        if now - self.rate_limiter["window_start"] > self.rate_limiter["time_window"]:
            self.rate_limiter["current_requests"] = 0
            self.rate_limiter["window_start"] = now
        
        if self.rate_limiter["current_requests"] >= self.rate_limiter["max_requests"]:
            return False
        
        self.rate_limiter["current_requests"] += 1
        return True
    
    def _check_circuit_breaker(self) -> bool:
        """Check circuit breaker state."""
        if self.circuit_breaker["state"] == CircuitState.OPEN:
            if (self.circuit_breaker["last_failure_time"] and 
                datetime.now() - self.circuit_breaker["last_failure_time"] >= 
                self.circuit_breaker["reset_timeout"]):
                self.circuit_breaker["state"] = CircuitState.HALF_OPEN
                return True
            return False
        return True
    
    def _get_from_cache(self, key: str) -> Optional[Dict]:
        """Get data from cache if not expired."""
        if key in self.cache["data"]:
            data, timestamp = self.cache["data"][key]
            if datetime.now() - timestamp <= self.cache["ttl"]:
                return data
            del self.cache["data"][key]
        return None
    
    def _update_cache(self, key: str, data: Dict):
        """Update cache with new data."""
        self.cache["data"][key] = (data, datetime.now())
    
    def _record_success(self):
        """Record successful API call."""
        if self.circuit_breaker["state"] == CircuitState.HALF_OPEN:
            self.circuit_breaker["state"] = CircuitState.CLOSED
        self.circuit_breaker["failures"] = 0
        self.metrics.successful_requests += 1
    
    def _record_failure(self):
        """Record failed API call."""
        self.circuit_breaker["failures"] += 1
        self.circuit_breaker["last_failure_time"] = datetime.now()
        if self.circuit_breaker["failures"] >= self.circuit_breaker["failure_threshold"]:
            self.circuit_breaker["state"] = CircuitState.OPEN
        self.metrics.failed_requests += 1
    
    def _update_metrics(self):
        """Update request metrics."""
        self.metrics.total_requests += 1
        self.metrics.last_request_time = datetime.now()
    
    async def _get_mock_data(self, zip_code: str, limit: int) -> List[Dict]:
        """Generate mock property data when needed."""
        try:
            # Check cache first
            cache_key = f"properties_{zip_code}"
            cached = self._get_from_cache(cache_key)
            if cached:
                return cached[:limit]
            
            # Generate mock properties
            properties = self._generate_properties(zip_code, limit)
            
            # Analyze market
            market_analysis = self.market_toolkit.analyze_market(
                zip_code,
                properties
            )
            
            # Identify opportunities for enrichment
            opportunities = self.market_toolkit.identify_opportunities(
                properties,
                market_analysis["market_analysis"]
            )
            
            # Selectively enrich high-scoring properties
            enriched_properties = []
            for prop in properties:
                # Check if property is a good opportunity
                is_opportunity = any(
                    o["id"] == prop["id"]
                    for o in opportunities
                )
                
                if is_opportunity and self.api_calls < self.api_limit:
                    # Enrich with ATTOM data
                    enriched = await self._enrich_property(prop)
                    enriched_properties.append(enriched)
                else:
                    enriched_properties.append(prop)
            
            # Cache results
            self._update_cache(cache_key, enriched_properties)
            
            return enriched_properties[:limit]
            
        except Exception as e:
            print(f"Error searching properties: {e}")
            return []
    
    def _generate_properties(
        self,
        zip_code: str,
        count: int
    ) -> List[Dict]:
        """Generate mock property data based on market characteristics."""
        try:
            properties = []
            market_data = self.market_toolkit.market_features.get(
                zip_code,
                {}
            )
            
            if not market_data:
                return []
            
            # Get property type distribution
            price_tier = market_data.get("price_tier", "moderate")
            type_dist = self.property_types.get(
                price_tier,
                self.property_types["moderate"]
            )
            
            for i in range(count):
                # Generate property with market-appropriate attributes
                property_type = self._weighted_choice(type_dist)
                
                property_data = {
                    "id": f"{zip_code}_{i}",
                    "address": self._generate_address(i),
                    "zip_code": zip_code,
                    "property_type": property_type,
                    "status": self._generate_status(),
                    "days_on_market": self._generate_dom(),
                    "data_source": "analyzer"
                }
                
                # Add market-adjusted attributes
                attributes = self.market_toolkit.generate_property_attributes(
                    zip_code,
                    property_type
                )
                property_data.update(attributes)
                
                properties.append(property_data)
            
            return properties
            
        except Exception as e:
            print(f"Error generating properties: {e}")
            return []
    
    async def _enrich_property(self, property_data: Dict) -> Dict:
        """Enrich property data with ATTOM API data."""
        try:
            # Check if we can make API call
            if self.api_calls >= self.api_limit:
                return property_data
            
            # Get ATTOM data
            attom_data = await self.attom_client.get_property_data(
                property_data["address"],
                property_data["zip_code"]
            )
            
            if attom_data:
                self.api_calls += 1
                property_data["attom_data"] = attom_data
                property_data["data_source"] = "ATTOM API"
            
            return property_data
            
        except Exception as e:
            print(f"Error enriching property: {e}")
            return property_data
    
    def _generate_address(self, index: int) -> str:
        """Generate a mock address."""
        streets = ["Main St", "Cedar Ln", "Pine Rd", "Maple Dr", "Elm St"]
        number = 1000 + (index * 437) % 9000  # Distributed numbers
        street = streets[index % len(streets)]
        return f"{number} {street}"
    
    def _generate_status(self) -> str:
        """Generate a property status."""
        statuses = ["For Sale", "Pending", "Just Listed"]
        weights = [0.5, 0.3, 0.2]
        return np.random.choice(statuses, p=weights)
    
    def _generate_dom(self) -> int:
        """Generate days on market."""
        return int(np.random.normal(30, 15))
    
    def _weighted_choice(self, options: Dict[str, float]) -> str:
        """Choose random item with weights."""
        items = list(options.keys())
        weights = list(options.values())
        return np.random.choice(items, p=weights)
