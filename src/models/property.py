from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PropertyLocation(BaseModel):
    address: str
    city: str
    state: str
    zipcode: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    
class PropertyFeatures(BaseModel):
    bedrooms: int
    bathrooms: float
    square_feet: int
    lot_size: Optional[int] = None
    year_built: int
    property_type: str
    stories: Optional[int] = None
    parking: Optional[str] = None
    amenities: List[str] = Field(default_factory=list)

class PropertyValuation(BaseModel):
    estimated_value: float
    confidence_score: float
    last_updated: datetime
    historical_values: List[Dict[str, float]] = Field(default_factory=list)
    comparable_properties: List[str] = Field(default_factory=list)
    valuation_factors: Dict[str, float] = Field(default_factory=dict)

class PropertyDetails(BaseModel):
    property_id: str
    location: PropertyLocation
    features: PropertyFeatures
    valuation: PropertyValuation
    last_sold: Optional[Dict[str, any]] = None
    tax_history: List[Dict[str, any]] = Field(default_factory=list)
    market_metrics: Dict[str, any] = Field(default_factory=dict)
    investment_metrics: Optional[Dict[str, any]] = None
    metadata: Dict[str, any] = Field(default_factory=dict)
