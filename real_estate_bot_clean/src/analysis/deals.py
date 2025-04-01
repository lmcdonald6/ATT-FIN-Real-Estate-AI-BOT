"""
Deal analysis module for real estate AI infrastructure.
Handles deal scoring, ARV calculations, and investment analysis.
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import logging
import asyncio
from datetime import datetime, timedelta
import numpy as np
from concurrent.futures import ThreadPoolExecutor

@dataclass
class PropertyMetrics:
    arv: float  # After Repair Value
    current_value: float
    repair_estimate: float
    equity: float
    rental_potential: float
    cap_rate: float
    cash_on_cash: float

@dataclass
class DealScore:
    overall_score: float
    profit_potential: float
    risk_level: float
    time_pressure: float
    competition_level: float
    financing_options: float

class DealAnalyzer:
    def __init__(self, cache_manager, sheets_manager, market_analyzer):
        self.logger = logging.getLogger(__name__)
        self.cache = cache_manager
        self.sheets = sheets_manager
        self.market = market_analyzer
        self._executor = ThreadPoolExecutor(max_workers=4)
        
        # Scoring weights
        self.WEIGHTS = {
            'profit': 0.35,
            'risk': 0.20,
            'time': 0.15,
            'competition': 0.15,
            'financing': 0.15
        }
        
        # Deal type thresholds
        self.DEAL_TYPES = {
            'wholesale': {'min_spread': 25000, 'min_equity': 0.3},
            'flip': {'min_roi': 0.25, 'max_repair': 0.4},
            'rental': {'min_cap_rate': 0.08, 'min_coc': 0.12}
        }

    async def analyze_deal(self, property_data: Dict) -> Tuple[PropertyMetrics, DealScore]:
        """Analyze a potential deal and calculate key metrics."""
        try:
            # Check cache first
            cache_key = f"deal_analysis_{property_data['property_id']}"
            cached_data = self.cache.get(cache_key, 'property')
            
            if cached_data:
                return cached_data
            
            # Calculate metrics
            metrics = await self._calculate_property_metrics(property_data)
            score = await self._score_deal(metrics, property_data)
            
            # Cache results
            result = (metrics, score)
            market_type = await self._get_market_type(property_data['zip_code'])
            self.cache.set(cache_key, result, 'property', market_type)
            
            return result
        except Exception as e:
            self.logger.error(f"Error analyzing deal: {e}")
            raise

    async def get_deal_type(self, metrics: PropertyMetrics, property_data: Dict) -> str:
        """Determine the best exit strategy for a deal."""
        # Calculate key ratios
        spread = metrics.arv - (property_data['list_price'] + metrics.repair_estimate)
        equity_ratio = (metrics.arv - property_data['list_price']) / metrics.arv
        repair_ratio = metrics.repair_estimate / metrics.arv
        
        # Check wholesale potential
        if (spread >= self.DEAL_TYPES['wholesale']['min_spread'] and 
            equity_ratio >= self.DEAL_TYPES['wholesale']['min_equity']):
            return 'wholesale'
        
        # Check flip potential
        roi = spread / (property_data['list_price'] + metrics.repair_estimate)
        if (roi >= self.DEAL_TYPES['flip']['min_roi'] and 
            repair_ratio <= self.DEAL_TYPES['flip']['max_repair']):
            return 'flip'
        
        # Check rental potential
        if (metrics.cap_rate >= self.DEAL_TYPES['rental']['min_cap_rate'] and 
            metrics.cash_on_cash >= self.DEAL_TYPES['rental']['min_coc']):
            return 'rental'
        
        return 'pass'  # Not a good deal for any strategy

    async def _calculate_property_metrics(self, property_data: Dict) -> PropertyMetrics:
        """Calculate detailed property metrics."""
        # Get comps data
        comps = await self._get_comps(property_data)
        
        # Calculate ARV using weighted comps
        arv = await self._calculate_arv(property_data, comps)
        
        # Estimate repairs
        repair_estimate = await self._estimate_repairs(property_data)
        
        # Calculate rental metrics
        rental_data = await self._analyze_rental_potential(property_data)
        
        return PropertyMetrics(
            arv=arv,
            current_value=property_data['list_price'],
            repair_estimate=repair_estimate,
            equity=arv - property_data['list_price'],
            rental_potential=rental_data['monthly_rent'],
            cap_rate=rental_data['cap_rate'],
            cash_on_cash=rental_data['cash_on_cash']
        )

    async def _score_deal(self, metrics: PropertyMetrics, property_data: Dict) -> DealScore:
        """Score a deal based on multiple factors."""
        # Calculate component scores (0-100)
        profit = self._calculate_profit_score(metrics)
        risk = self._calculate_risk_score(metrics, property_data)
        time = self._calculate_time_pressure(property_data)
        competition = await self._analyze_competition(property_data)
        financing = self._calculate_financing_options(metrics, property_data)
        
        # Calculate overall score
        overall = (
            profit * self.WEIGHTS['profit'] +
            (100 - risk) * self.WEIGHTS['risk'] +  # Invert risk
            time * self.WEIGHTS['time'] +
            (100 - competition) * self.WEIGHTS['competition'] +  # Invert competition
            financing * self.WEIGHTS['financing']
        )
        
        return DealScore(
            overall_score=overall,
            profit_potential=profit,
            risk_level=risk,
            time_pressure=time,
            competition_level=competition,
            financing_options=financing
        )

    def _calculate_profit_score(self, metrics: PropertyMetrics) -> float:
        """Calculate profit potential score."""
        # Base score on equity percentage
        equity_ratio = metrics.equity / metrics.arv
        base_score = min(100, equity_ratio * 200)  # 50% equity = 100 points
        
        # Adjust for repair ratio
        repair_ratio = metrics.repair_estimate / metrics.arv
        repair_penalty = max(0, (repair_ratio - 0.2) * 100)  # Penalty starts at 20% repair ratio
        
        return max(0, base_score - repair_penalty)

    def _calculate_risk_score(self, metrics: PropertyMetrics, property_data: Dict) -> float:
        """Calculate risk level score."""
        risk_factors = {
            'repair_ratio': metrics.repair_estimate / metrics.arv,
            'price_volatility': property_data.get('price_volatility', 0.1),
            'days_on_market': property_data.get('days_on_market', 30) / 90,
            'title_issues': 1 if property_data.get('title_issues') else 0,
            'occupancy': 1 if property_data.get('occupied') else 0
        }
        
        weights = {
            'repair_ratio': 0.3,
            'price_volatility': 0.2,
            'days_on_market': 0.2,
            'title_issues': 0.15,
            'occupancy': 0.15
        }
        
        return sum(score * weights[factor] * 100 for factor, score in risk_factors.items())

    async def _get_market_type(self, zip_code: str) -> str:
        """Get market type for caching strategy."""
        metrics, _ = await self.market.analyze_market(zip_code)
        return self.market.get_market_type(metrics)

    async def _get_comps(self, property_data: Dict) -> List[Dict]:
        """Get comparable properties from cache or sheets."""
        cache_key = f"comps_{property_data['zip_code']}_{property_data['bedrooms']}"
        comps = self.cache.get(cache_key, 'property')
        
        if not comps:
            comps = await self.sheets.get_comps(
                property_data['zip_code'],
                property_data['bedrooms'],
                property_data['square_feet']
            )
            self.cache.set(cache_key, comps, 'property')
        
        return comps

    async def _calculate_arv(self, property_data: Dict, comps: List[Dict]) -> float:
        """Calculate After Repair Value using weighted comps."""
        if not comps:
            raise ValueError("No comparable properties found")
        
        # Calculate similarity scores
        similarities = []
        for comp in comps:
            score = self._calculate_similarity(property_data, comp)
            similarities.append((comp, score))
        
        # Sort by similarity and take top 5
        similarities.sort(key=lambda x: x[1], reverse=True)
        top_comps = similarities[:5]
        
        # Calculate weighted average
        total_weight = sum(score for _, score in top_comps)
        arv = sum(comp['sale_price'] * (score / total_weight) 
                 for comp, score in top_comps)
        
        return arv

    def _calculate_similarity(self, subject: Dict, comp: Dict) -> float:
        """Calculate similarity score between two properties."""
        factors = {
            'square_feet': (0.3, 0.1),  # (weight, tolerance)
            'bedrooms': (0.2, 0),
            'bathrooms': (0.2, 0),
            'year_built': (0.15, 10),
            'lot_size': (0.15, 0.2)
        }
        
        score = 0
        for factor, (weight, tolerance) in factors.items():
            if subject.get(factor) and comp.get(factor):
                diff = abs(subject[factor] - comp[factor])
                if tolerance == 0:  # Exact match required
                    score += weight if diff == 0 else 0
                else:
                    factor_score = max(0, 1 - (diff / (subject[factor] * tolerance)))
                    score += weight * factor_score
        
        return score

    async def _estimate_repairs(self, property_data: Dict) -> float:
        """Estimate repair costs based on property condition."""
        base_sqft_cost = 20  # Base repair cost per sqft
        
        condition_multipliers = {
            'excellent': 0,
            'good': 0.3,
            'fair': 0.6,
            'poor': 1.0,
            'unknown': 0.7
        }
        
        condition = property_data.get('condition', 'unknown').lower()
        multiplier = condition_multipliers.get(condition, 0.7)
        
        return property_data['square_feet'] * base_sqft_cost * multiplier

    async def _analyze_rental_potential(self, property_data: Dict) -> Dict:
        """Analyze rental potential and returns."""
        # Get rental comps
        rental_comps = await self._get_rental_comps(property_data)
        
        if not rental_comps:
            return {
                'monthly_rent': 0,
                'cap_rate': 0,
                'cash_on_cash': 0
            }
        
        # Calculate average rent
        monthly_rent = np.median([comp['monthly_rent'] for comp in rental_comps])
        
        # Calculate returns
        annual_rent = monthly_rent * 12
        expenses = self._estimate_expenses(property_data, annual_rent)
        noi = annual_rent - expenses
        
        total_investment = (
            property_data['list_price'] + 
            await self._estimate_repairs(property_data)
        )
        
        cap_rate = noi / total_investment
        
        # Assume 75% LTV financing
        down_payment = total_investment * 0.25
        monthly_payment = self._calculate_mortgage_payment(total_investment * 0.75)
        annual_cash_flow = noi - (monthly_payment * 12)
        cash_on_cash = annual_cash_flow / down_payment
        
        return {
            'monthly_rent': monthly_rent,
            'cap_rate': cap_rate,
            'cash_on_cash': cash_on_cash
        }

    def _estimate_expenses(self, property_data: Dict, annual_rent: float) -> float:
        """Estimate annual property expenses."""
        expense_ratios = {
            'vacancy': 0.08,
            'maintenance': 0.10,
            'management': 0.10,
            'taxes': 0.15,
            'insurance': 0.05
        }
        
        return sum(ratio * annual_rent for ratio in expense_ratios.values())

    def _calculate_mortgage_payment(self, loan_amount: float) -> float:
        """Calculate monthly mortgage payment."""
        rate = 0.06 / 12  # 6% annual rate
        term = 30 * 12    # 30 years
        
        return (loan_amount * rate * (1 + rate)**term) / ((1 + rate)**term - 1)

    async def _analyze_competition(self, property_data: Dict) -> float:
        """Analyze competition level in the area."""
        market_metrics, _ = await self.market.analyze_market(property_data['zip_code'])
        
        # Higher score = more competition
        competition_score = (
            min(100, market_metrics.inventory_level * 20) * 0.4 +  # Inventory level
            min(100, max(0, -market_metrics.price_trend * 200)) * 0.3 +  # Price trends
            min(100, market_metrics.days_on_market / 1.2) * 0.3  # Days on market
        )
        
        return competition_score

    def _calculate_financing_options(self, metrics: PropertyMetrics, property_data: Dict) -> float:
        """Calculate financing options score."""
        # Base score on LTV ratio
        ltv = property_data['list_price'] / metrics.arv
        base_score = 100 - min(100, ltv * 100)  # Lower LTV = higher score
        
        # Adjust for property condition
        condition_penalties = {
            'excellent': 0,
            'good': 10,
            'fair': 25,
            'poor': 50,
            'unknown': 30
        }
        condition = property_data.get('condition', 'unknown').lower()
        penalty = condition_penalties.get(condition, 30)
        
        return max(0, base_score - penalty)

    def __del__(self):
        """Cleanup executor on deletion."""
        self._executor.shutdown(wait=False)
