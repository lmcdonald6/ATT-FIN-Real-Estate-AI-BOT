from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime

class PriceTrend(BaseModel):
    timeframe: str
    average_price: float
    median_price: float
    price_per_sqft: float
    year_over_year_change: float
    month_over_month_change: float
    historical_prices: List[Dict[str, float]]

class MarketInventory(BaseModel):
    active_listings: int
    new_listings: int
    price_reduced: int
    days_on_market: float
    months_of_supply: float
    absorption_rate: float

class Demographics(BaseModel):
    population: int
    median_age: float
    median_income: float
    population_growth: float
    household_size: float
    education_level: Dict[str, float]
    employment_stats: Dict[str, float]

class EconomicIndicators(BaseModel):
    unemployment_rate: float
    job_growth: float
    income_growth: float
    business_growth: float
    economic_health_score: float

class MarketAnalysis(BaseModel):
    zipcode: str
    last_updated: datetime
    price_trends: PriceTrend
    inventory: MarketInventory
    demographics: Demographics
    economic_indicators: EconomicIndicators
    market_score: float
    risk_level: str
    opportunity_score: float
    metadata: Dict[str, any] = Field(default_factory=dict)

class PriceForecast(BaseModel):
    forecast_period: str
    predicted_values: List[Dict[str, float]]
    confidence_interval: Dict[str, List[float]]
    forecast_factors: Dict[str, float]

class DemandForecast(BaseModel):
    forecast_period: str
    predicted_demand: List[Dict[str, float]]
    seasonal_factors: Dict[str, float]
    demand_drivers: List[Dict[str, any]]

class RiskFactor(BaseModel):
    category: str
    risk_level: str
    description: str
    impact_score: float
    mitigation_strategies: List[str]

class MarketOpportunity(BaseModel):
    category: str
    description: str
    potential_return: float
    confidence_score: float
    required_capital: Optional[float]
    timeframe: str

class TrendAnalysis(BaseModel):
    zipcode: str
    analysis_date: datetime
    price_forecast: PriceForecast
    demand_forecast: DemandForecast
    risk_factors: List[RiskFactor]
    opportunities: List[MarketOpportunity]
    confidence_score: float
    metadata: Dict[str, any] = Field(default_factory=dict)
