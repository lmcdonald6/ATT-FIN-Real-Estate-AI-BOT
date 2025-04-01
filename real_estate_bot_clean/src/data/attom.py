"""
ATTOM API client with rate limiting and retry logic.
Monthly limit: 400 reports
"""
import logging
import aiohttp
import asyncio
import os
from datetime import datetime, timedelta
from typing import Dict, Optional
from ..utils.rate_limiter import RateLimiter

class AttomClient:
    """Client for ATTOM API with rate limiting and retry logic."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.api_key = os.getenv('ATTOM_API_KEY', '')
        self.base_url = "https://api.attomdata.com/property/v1"
        
        # Rate limiting setup
        self.monthly_limit = 400
        self.rate_limiter = RateLimiter(
            self.monthly_limit,
            timedelta(days=30)
        )
        
        # Retry configuration
        self.max_retries = 3
        self.retry_delay = 1  # seconds
        self.retry_codes = {500, 502, 503, 504}  # Server errors
        
        # Track usage
        self.usage_start = datetime.now()
        self.calls_made = 0
    
    async def get_property_data(self, address: str,
                              zip_code: str) -> Optional[Dict]:
        """
        Get property data from ATTOM API.
        Implements retry logic and rate limiting.
        """
        if not self.api_key:
            self.logger.error("No ATTOM API key provided")
            return None
        
        # Check rate limit
        if not await self.rate_limiter.acquire():
            self.logger.warning("Monthly API limit reached")
            return None
        
        headers = {
            "apikey": self.api_key,
            "accept": "application/json"
        }
        
        property_url = f"{self.base_url}/property/detail"
        params = {
            "address": address,
            "zipcode": zip_code
        }
        
        # Implement retry logic
        for attempt in range(self.max_retries):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        property_url,
                        headers=headers,
                        params=params
                    ) as resp:
                        # Track API usage
                        self.calls_made += 1
                        
                        if resp.status == 200:
                            data = await resp.json()
                            return self._process_response(data)
                        
                        elif resp.status == 429:  # Rate limit
                            self.logger.warning("Rate limit hit")
                            return None
                        
                        elif resp.status in self.retry_codes:
                            if attempt < self.max_retries - 1:
                                await asyncio.sleep(
                                    self.retry_delay * (attempt + 1)
                                )
                                continue
                        
                        self.logger.error(
                            f"ATTOM API error: {resp.status} - {await resp.text()}"
                        )
                        return None
            
            except Exception as e:
                self.logger.error(f"Error calling ATTOM API: {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (attempt + 1))
                    continue
                return None
        
        return None
    
    def _process_response(self, response: Dict) -> Dict:
        """Process ATTOM API response."""
        try:
            property_data = response.get('property', {})
            return {
                # Core property data
                "property_id": property_data.get('identifier', {}).get('attomId'),
                "lot_size": property_data.get('lot', {}).get('lotSize'),
                "zoning": property_data.get('lot', {}).get('zoning'),
                
                # Assessment data
                "tax_assessment": property_data.get('assessment', {}).get('assessed'),
                "tax_amount": property_data.get('assessment', {}).get('tax'),
                "tax_year": property_data.get('assessment', {}).get('taxYear'),
                
                # Market data
                "avm_value": property_data.get('avm', {}).get('amount'),
                "confidence_score": property_data.get('avm', {}).get('confidence'),
                "forecast_standard_deviation": property_data.get('avm', {}).get('standardDeviation'),
                
                # Rental data
                "rental_yield": property_data.get('rental', {}).get('yield'),
                "estimated_rent": property_data.get('rental', {}).get('estimatedRent'),
                
                # Metadata
                "last_updated": datetime.now().isoformat(),
                "source": "attom"
            }
        
        except Exception as e:
            self.logger.error(f"Error processing ATTOM response: {e}")
            return {}
