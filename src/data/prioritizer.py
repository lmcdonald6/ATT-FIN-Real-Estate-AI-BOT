"""Data Prioritizer for Real Estate Analysis"""
from typing import Dict, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class DataPrioritizer:
    """Prioritizes and combines data from multiple sources"""
    
    def __init__(self):
        self.confidence_thresholds = {
            'high': 0.8,
            'medium': 0.6,
            'low': 0.4
        }
        
        # Scoring weights for different property aspects
        self.scoring_weights = {
            'distress_indicators': 0.25,  # High weight for distress signs
            'equity_position': 0.20,      # Strong equity is important
            'market_potential': 0.15,     # Market growth potential
            'property_condition': 0.15,   # Physical condition
            'owner_motivation': 0.15,     # Signs of motivated seller
            'location_score': 0.10        # Location quality
        }
        
        # Distress indicator weights
        self.distress_weights = {
            'tax_delinquent': 0.25,
            'foreclosure': 0.25,
            'high_vacancy_risk': 0.15,
            'code_violations': 0.15,
            'mortgage_default': 0.20
        }
    
    async def get_property_data(self, address: str, zipcode: str) -> Dict:
        """
        Get comprehensive property data with prioritization:
        1. ATTOM API (primary source)
        2. Redfin data (market trends)
        3. Local tax assessor data
        4. Historical sales data
        """
        try:
            property_data = {
                'address': address,
                'zipcode': zipcode,
                'data_sources': [],
                'confidence_scores': {},
                'last_updated': datetime.now().isoformat()
            }
            
            # Collect data from each source
            attom_data = await self._get_attom_data(address, zipcode)
            if attom_data:
                property_data.update(attom_data)
                property_data['data_sources'].append('ATTOM')
                property_data['confidence_scores']['ATTOM'] = self._calculate_confidence(attom_data)
            
            redfin_data = await self._get_redfin_data(address, zipcode)
            if redfin_data:
                self._merge_market_data(property_data, redfin_data)
                property_data['data_sources'].append('Redfin')
                property_data['confidence_scores']['Redfin'] = self._calculate_confidence(redfin_data)
            
            tax_data = await self._get_tax_data(address, zipcode)
            if tax_data:
                self._merge_tax_data(property_data, tax_data)
                property_data['data_sources'].append('Tax Assessor')
                property_data['confidence_scores']['Tax Assessor'] = self._calculate_confidence(tax_data)
            
            # Calculate overall confidence score
            property_data['overall_confidence'] = self._calculate_overall_confidence(
                property_data['confidence_scores']
            )
            
            return property_data
            
        except Exception as e:
            logger.error(f"Error getting property data: {str(e)}")
            raise
    
    async def _get_attom_data(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get property data from ATTOM API"""
        try:
            # Implement ATTOM API call
            return {
                'property_details': {
                    'beds': 3,
                    'baths': 2,
                    'sqft': 1500,
                    'year_built': 1990,
                    'lot_size': 0.25
                },
                'market_data': {
                    'estimated_value': 200000,
                    'last_sale_price': 180000,
                    'last_sale_date': '2020-01-01',
                    'days_on_market': 75
                },
                'owner_info': {
                    'owner_type': 'absentee',
                    'owner_name': 'John Doe',
                    'mailing_address': '456 Different St'
                },
                'distress_indicators': {
                    'indicators': ['tax_delinquent', 'high_vacancy_risk'],
                    'severity': 'medium'
                }
            }
        except Exception as e:
            logger.error(f"Error getting ATTOM data: {str(e)}")
            return None
    
    async def _get_redfin_data(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get market data from Redfin"""
        try:
            # Implement Redfin API call
            return {
                'market_trends': {
                    'median_price': 195000,
                    'price_trend': '+5.2%',
                    'days_on_market_avg': 45,
                    'inventory_level': 'low'
                }
            }
        except Exception as e:
            logger.error(f"Error getting Redfin data: {str(e)}")
            return None
    
    async def _get_tax_data(self, address: str, zipcode: str) -> Optional[Dict]:
        """Get tax assessor data"""
        try:
            # Implement tax assessor data retrieval
            return {
                'tax_assessment': {
                    'assessed_value': 175000,
                    'tax_amount': 2100,
                    'tax_year': 2024,
                    'tax_status': 'delinquent'
                }
            }
        except Exception as e:
            logger.error(f"Error getting tax data: {str(e)}")
            return None
    
    def _merge_market_data(self, property_data: Dict, market_data: Dict) -> None:
        """Merge market data into property data"""
        if 'market_data' not in property_data:
            property_data['market_data'] = {}
        
        property_data['market_data'].update(market_data.get('market_trends', {}))
    
    def _merge_tax_data(self, property_data: Dict, tax_data: Dict) -> None:
        """Merge tax data into property data"""
        if 'tax_assessment' not in property_data:
            property_data['tax_assessment'] = {}
        
        property_data['tax_assessment'].update(tax_data.get('tax_assessment', {}))
    
    def _calculate_confidence(self, data: Dict) -> float:
        """Calculate confidence score for a data source"""
        if not data:
            return 0.0
        
        # Count non-empty fields
        total_fields = 0
        non_empty_fields = 0
        
        for key, value in data.items():
            if isinstance(value, dict):
                for sub_key, sub_value in value.items():
                    total_fields += 1
                    if sub_value is not None:
                        non_empty_fields += 1
            else:
                total_fields += 1
                if value is not None:
                    non_empty_fields += 1
        
        return non_empty_fields / total_fields if total_fields > 0 else 0.0
    
    def _calculate_overall_confidence(self, scores: Dict[str, float]) -> float:
        """Calculate overall confidence score"""
        if not scores:
            return 0.0
        
        # Weight the scores based on source reliability
        weights = {
            'ATTOM': 0.5,
            'Redfin': 0.3,
            'Tax Assessor': 0.2
        }
        
        weighted_sum = 0
        total_weight = 0
        
        for source, score in scores.items():
            weight = weights.get(source, 0.1)
            weighted_sum += score * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def score_property(self, property_data: Dict) -> float:
        """Score a property based on investment potential"""
        try:
            scores = {}
            
            # 1. Score distress indicators
            scores['distress_indicators'] = self._score_distress(
                property_data.get('distress_indicators', [])
            )
            
            # 2. Score equity position
            scores['equity_position'] = self._score_equity(
                property_data.get('price', 0),
                property_data.get('estimated_value', 0),
                property_data.get('equity_percentage', 0)
            )
            
            # 3. Score market potential
            scores['market_potential'] = self._score_market(
                property_data.get('days_on_market', 0),
                property_data.get('market_data', {})
            )
            
            # 4. Score property condition
            scores['property_condition'] = self._score_condition(
                property_data.get('year_built', 0),
                property_data.get('last_renovation', 0),
                property_data.get('condition_score', 0)
            )
            
            # 5. Score owner motivation
            scores['owner_motivation'] = self._score_motivation(
                property_data.get('owner_type', ''),
                property_data.get('owner_info', {}),
                property_data.get('listing_history', [])
            )
            
            # 6. Score location
            scores['location_score'] = self._score_location(
                property_data.get('location_metrics', {})
            )
            
            # Calculate weighted average
            final_score = 0
            for aspect, score in scores.items():
                weight = self.scoring_weights.get(aspect, 0)
                final_score += score * weight
            
            # Normalize to 0-100 scale
            return round(final_score * 100)
            
        except Exception as e:
            logger.error(f"Error scoring property: {str(e)}")
            return 0
    
    def _score_distress(self, indicators: List[str]) -> float:
        """Score property based on distress indicators"""
        if not indicators:
            return 0.0
            
        score = 0
        for indicator in indicators:
            score += self.distress_weights.get(indicator, 0)
            
        return min(score, 1.0)  # Cap at 1.0
    
    def _score_equity(self, price: float, value: float, equity_pct: float) -> float:
        """Score property based on equity position"""
        if not all([price, value, equity_pct]):
            return 0.0
            
        # Higher score for properties with more equity
        equity_score = min(equity_pct / 100, 1.0)
        
        # Bonus for good discount to value
        if price and value:
            discount = (value - price) / value
            discount_score = min(discount, 0.5)  # Cap discount bonus at 0.5
            return min(equity_score + discount_score, 1.0)
            
        return equity_score
    
    def _score_market(self, days_on_market: int, market_data: Dict) -> float:
        """Score property based on market conditions"""
        score = 0.0
        
        # Days on market score (higher for longer DOM)
        if days_on_market:
            dom_score = min(days_on_market / 180, 1.0)  # Cap at 180 days
            score += dom_score * 0.4  # 40% weight
        
        # Market trends score
        if market_data:
            # Positive price trends
            price_trend = float(market_data.get('price_trend', '0').strip('%')) / 100
            if price_trend > 0:
                score += min(price_trend, 0.3)  # 30% weight
            
            # Supply/demand score
            if market_data.get('supply_demand') == 'Low Supply':
                score += 0.3  # 30% weight
        
        return min(score, 1.0)
    
    def _score_condition(self, year_built: int, last_renovation: int, condition_score: float) -> float:
        """Score property based on physical condition"""
        if not year_built:
            return 0.0
            
        score = 0.0
        current_year = datetime.now().year
        
        # Age score (newer = lower score, we want older properties)
        age = current_year - year_built
        age_score = min(age / 50, 1.0)  # Cap at 50 years
        score += age_score * 0.4  # 40% weight
        
        # Renovation needs (no recent renovation = higher score)
        if last_renovation:
            years_since_reno = current_year - last_renovation
            reno_score = min(years_since_reno / 20, 1.0)  # Cap at 20 years
            score += reno_score * 0.3  # 30% weight
        
        # Condition score (lower condition = higher score)
        if condition_score:
            condition_score = 1 - (condition_score / 100)  # Invert so worse condition = higher score
            score += condition_score * 0.3  # 30% weight
        
        return min(score, 1.0)
    
    def _score_motivation(self, owner_type: str, owner_info: Dict, listing_history: List) -> float:
        """Score property based on owner motivation signals"""
        score = 0.0
        
        # Owner type score
        if owner_type == 'absentee':
            score += 0.4  # 40% weight
        
        # Multiple property owner (more properties = higher motivation)
        portfolio_size = owner_info.get('portfolio_size', 0)
        if portfolio_size > 1:
            portfolio_score = min(portfolio_size / 10, 1.0)  # Cap at 10 properties
            score += portfolio_score * 0.3  # 30% weight
        
        # Listing history (price reductions = higher motivation)
        if listing_history:
            price_cuts = sum(1 for listing in listing_history if listing.get('price_reduced', False))
            price_cut_score = min(price_cuts / 3, 1.0)  # Cap at 3 price cuts
            score += price_cut_score * 0.3  # 30% weight
        
        return min(score, 1.0)
    
    def _score_location(self, metrics: Dict) -> float:
        """Score property based on location quality"""
        if not metrics:
            return 0.0
            
        score = 0.0
        
        # Neighborhood score
        neighborhood_score = metrics.get('neighborhood_score', 0) / 100
        score += neighborhood_score * 0.4  # 40% weight
        
        # Crime rate (higher crime = higher score)
        crime_rate = metrics.get('crime_rate', 0) / 100
        score += crime_rate * 0.3  # 30% weight
        
        # Vacancy rate (higher vacancy = higher score)
        vacancy_rate = metrics.get('vacancy_rate', 0) / 100
        score += vacancy_rate * 0.3  # 30% weight
        
        return min(score, 1.0)
