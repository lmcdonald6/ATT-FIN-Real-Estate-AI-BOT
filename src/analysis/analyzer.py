from typing import Dict, List
import logging
from datetime import datetime

class PropertyAnalyzer:
    """Unified property analysis system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def analyze(self, property_data: Dict) -> Dict:
        """Comprehensive property analysis"""
        try:
            return {
                'property_value': self._analyze_value(property_data),
                'property_details': self._analyze_details(property_data),
                'tax_assessment': self._analyze_tax(property_data),
                'owner_info': self._analyze_owner(property_data),
                'occupancy': self._analyze_occupancy(property_data),
                'distress_indicators': self._analyze_distress(property_data),
                'investment_metrics': self._analyze_investment(property_data)
            }
        except Exception as e:
            self.logger.error(f"Error in property analysis: {str(e)}")
            raise
    
    def _analyze_value(self, data: Dict) -> Dict:
        """Analyze property value"""
        return {
            'estimated_value': data.get('avm_value', 0),
            'confidence_score': data.get('avm_confidence', 'N/A'),
            'price_trend': data.get('price_trend', 'stable'),
            'equity_position': data.get('estimated_equity', 'N/A')
        }
    
    def _analyze_details(self, data: Dict) -> Dict:
        """Analyze property details"""
        return {
            'basic_info': {
                'beds': data.get('beds', 0),
                'baths': data.get('baths', 0),
                'sqft': data.get('sqft', 0),
                'year_built': data.get('year_built', 0)
            },
            'construction': {
                'foundation': data.get('foundation_type', 'N/A'),
                'roof': data.get('roof_type', 'N/A'),
                'systems': data.get('systems', {})
            }
        }
    
    def _analyze_tax(self, data: Dict) -> Dict:
        """Analyze tax assessment"""
        return {
            'current_value': data.get('tax_assessment', 0),
            'market_comparison': data.get('assessment_ratio', 'N/A'),
            'tax_history': data.get('tax_history', []),
            'status': data.get('tax_status', 'Unknown')
        }
    
    def _analyze_owner(self, data: Dict) -> Dict:
        """Analyze owner information"""
        return {
            'current_owner': data.get('owner_name', 'N/A'),
            'ownership_length': data.get('ownership_length', 'N/A'),
            'portfolio_size': data.get('owner_properties', 0),
            'estimated_equity': data.get('estimated_equity', 'N/A')
        }
    
    def _analyze_occupancy(self, data: Dict) -> Dict:
        """Analyze occupancy status"""
        return {
            'status': data.get('occupancy_status', 'Unknown'),
            'vacancy_risk': self._calculate_vacancy_risk(data),
            'utility_status': data.get('utility_status', 'Unknown'),
            'mail_status': data.get('mail_status', 'Unknown')
        }
    
    def _analyze_distress(self, data: Dict) -> Dict:
        """Analyze distress indicators"""
        return {
            'foreclosure_status': {
                'status': data.get('foreclosure_status', 'None'),
                'stage': data.get('foreclosure_stage', 'N/A'),
                'auction_date': data.get('auction_date', 'N/A'),
                'default_amount': data.get('default_amount', 'N/A')
            },
            'liens_bankruptcy': {
                'total_liens': data.get('lien_count', 0),
                'lien_amount': data.get('total_liens', 'N/A'),
                'bankruptcy_status': data.get('bankruptcy_status', 'None'),
                'risk_level': self._calculate_distress_risk(data)
            }
        }
    
    def analyze_market(self, market_data: Dict) -> Dict:
        """Analyze market conditions"""
        try:
            return {
                'price_trends': {
                    'median_price': market_data.get('median_price', 0),
                    'price_change': market_data.get('price_change_1yr', 'N/A'),
                    'forecast_12m': market_data.get('price_forecast', 'N/A')
                },
                'sales_metrics': {
                    'monthly_sales': market_data.get('monthly_sales', 0),
                    'days_on_market': market_data.get('avg_dom', 0),
                    'absorption_rate': market_data.get('absorption_rate', 'N/A')
                },
                'market_health': {
                    'inventory_months': market_data.get('months_inventory', 0),
                    'price_reductions': market_data.get('price_reduced_pct', 'N/A'),
                    'market_condition': self._determine_market_condition(market_data)
                }
            }
        except Exception as e:
            self.logger.error(f"Error in market analysis: {str(e)}")
            raise
    
    def analyze_investment(self, data: Dict) -> Dict:
        """Analyze investment potential"""
        try:
            arv = self._calculate_arv(data)
            repair_cost = self._estimate_repairs(data)
            
            return {
                'arv_analysis': {
                    'estimated_arv': arv,
                    'confidence_score': data.get('arv_confidence', 'N/A'),
                    'comp_count': len(data.get('comps', [])),
                    'best_comps': self._get_best_comps(data)
                },
                'repair_estimate': {
                    'total_cost': repair_cost,
                    'major_items': data.get('repair_items', []),
                    'contingency': repair_cost * 0.1
                },
                'deal_metrics': {
                    'mao': self._calculate_mao(data),
                    'potential_profit': arv - data.get('price', 0) - repair_cost,
                    'roi': self._calculate_roi(data, arv, repair_cost),
                    'deal_score': self._calculate_deal_score(data, arv, repair_cost)
                }
            }
        except Exception as e:
            self.logger.error(f"Error in investment analysis: {str(e)}")
            raise
    
    def score_lead(self, data: Dict) -> Dict:
        """Score potential lead"""
        try:
            financial_score = self._score_financial_distress(data)
            time_score = self._score_time_pressure(data)
            condition_score = self._score_property_condition(data)
            market_score = self._score_market_position(data)
            
            total_score = (
                financial_score * 0.35 +
                time_score * 0.25 +
                condition_score * 0.20 +
                market_score * 0.20
            )
            
            return {
                'total_score': round(total_score),
                'components': {
                    'financial_distress': round(financial_score),
                    'time_pressure': round(time_score),
                    'property_condition': round(condition_score),
                    'market_position': round(market_score)
                },
                'status': self._get_lead_status(total_score),
                'recommended_actions': self._get_recommended_actions(data, total_score)
            }
        except Exception as e:
            self.logger.error(f"Error in lead scoring: {str(e)}")
            raise
    
    def _calculate_vacancy_risk(self, data: Dict) -> str:
        """Calculate vacancy risk level"""
        risk_factors = 0
        
        if not data.get('utility_status') == 'Active':
            risk_factors += 1
        if not data.get('mail_status') == 'Active':
            risk_factors += 1
        if data.get('last_sale_date'):
            last_sale = datetime.strptime(data['last_sale_date'], '%Y-%m-%d')
            if (datetime.now() - last_sale).days > 365:
                risk_factors += 1
                
        return 'High' if risk_factors >= 2 else 'Medium' if risk_factors == 1 else 'Low'
    
    def _calculate_distress_risk(self, data: Dict) -> str:
        """Calculate overall distress risk"""
        risk_factors = 0
        
        if data.get('foreclosure_status') != 'None':
            risk_factors += 2
        if data.get('lien_count', 0) > 0:
            risk_factors += 1
        if data.get('tax_delinquent', False):
            risk_factors += 1
        if data.get('bankruptcy_status') != 'None':
            risk_factors += 2
            
        return 'High' if risk_factors >= 3 else 'Medium' if risk_factors >= 1 else 'Low'
    
    def _determine_market_condition(self, data: Dict) -> str:
        """Determine overall market condition"""
        months_inventory = data.get('months_inventory', 6)
        price_trend = data.get('price_trend', 0)
        dom = data.get('avg_dom', 45)
        
        if months_inventory <= 3 and price_trend > 0 and dom < 30:
            return "Seller's Market"
        elif months_inventory >= 6 and price_trend < 0 and dom > 60:
            return "Buyer's Market"
        else:
            return "Balanced Market"
    
    def _calculate_arv(self, data: Dict) -> float:
        """Calculate After Repair Value"""
        comps = data.get('comps', [])
        if not comps:
            return data.get('avm_value', 0)
            
        # Weight recent sales more heavily
        weighted_values = []
        total_weight = 0
        
        for comp in comps:
            days_old = (datetime.now() - datetime.strptime(comp['sale_date'], '%Y-%m-%d')).days
            weight = 1.0 if days_old <= 90 else 0.8 if days_old <= 180 else 0.6
            weighted_values.append(comp['sale_price'] * weight)
            total_weight += weight
            
        return sum(weighted_values) / total_weight if total_weight > 0 else 0
    
    def _estimate_repairs(self, data: Dict) -> float:
        """Estimate repair costs"""
        repair_items = data.get('repair_items', [])
        systems = data.get('systems', {})
        
        total_cost = 0
        
        # Major systems
        if systems.get('roof') == 'Poor':
            total_cost += 8000
        if systems.get('hvac') == 'Poor':
            total_cost += 6000
        if systems.get('plumbing') == 'Poor':
            total_cost += 5000
        if systems.get('electrical') == 'Poor':
            total_cost += 4000
            
        # Add costs for specific repair items
        for item in repair_items:
            total_cost += item.get('cost', 0)
            
        # Add contingency
        total_cost *= 1.1
        
        return total_cost
    
    def _calculate_mao(self, data: Dict) -> float:
        """Calculate Maximum Allowable Offer"""
        arv = self._calculate_arv(data)
        repair_cost = self._estimate_repairs(data)
        holding_costs = data.get('holding_costs', 0)
        
        # 70% ARV Rule
        mao = (arv * 0.70) - repair_cost - holding_costs
        return max(mao, 0)
    
    def _calculate_roi(self, data: Dict, arv: float, repair_cost: float) -> float:
        """Calculate Return on Investment"""
        purchase_price = data.get('price', 0)
        if not purchase_price:
            return 0
            
        total_cost = purchase_price + repair_cost
        profit = arv - total_cost
        
        return (profit / total_cost) * 100 if total_cost > 0 else 0
    
    def _calculate_deal_score(self, data: Dict, arv: float, repair_cost: float) -> int:
        """Calculate overall deal score"""
        score = 0
        purchase_price = data.get('price', 0)
        
        # ARV to Purchase Price Ratio (30 points)
        if purchase_price and arv:
            ratio = purchase_price / arv
            if ratio <= 0.65:
                score += 30
            elif ratio <= 0.75:
                score += 20
            elif ratio <= 0.85:
                score += 10
                
        # Repair Cost to ARV Ratio (20 points)
        if repair_cost and arv:
            ratio = repair_cost / arv
            if ratio <= 0.15:
                score += 20
            elif ratio <= 0.25:
                score += 15
            elif ratio <= 0.35:
                score += 10
                
        # Potential ROI (30 points)
        roi = self._calculate_roi(data, arv, repair_cost)
        if roi >= 30:
            score += 30
        elif roi >= 20:
            score += 20
        elif roi >= 15:
            score += 10
            
        # Market Condition (20 points)
        market_condition = data.get('market_condition', '')
        if market_condition == "Seller's Market":
            score += 20
        elif market_condition == "Balanced Market":
            score += 15
        else:
            score += 10
            
        return score
    
    def _get_best_comps(self, data: Dict) -> List[Dict]:
        """Get best comparable properties"""
        comps = data.get('comps', [])
        if not comps:
            return []
            
        # Sort by similarity score and recency
        sorted_comps = sorted(
            comps,
            key=lambda x: (x.get('similarity', 0), 
                         -abs((datetime.now() - datetime.strptime(x['sale_date'], '%Y-%m-%d')).days)),
            reverse=True
        )
        
        return sorted_comps[:3]  # Return top 3 comps
    
    def _score_financial_distress(self, data: Dict) -> float:
        """Score financial distress indicators"""
        score = 0
        
        # Foreclosure status (40 points)
        if data.get('foreclosure_status') == 'Pre-foreclosure':
            score += 40
        elif data.get('foreclosure_status') == 'Notice of Default':
            score += 30
            
        # Tax delinquency (20 points)
        if data.get('tax_delinquent', False):
            score += 20
            
        # Liens (20 points)
        lien_count = data.get('lien_count', 0)
        if lien_count > 2:
            score += 20
        elif lien_count > 0:
            score += 10
            
        # Negative equity (20 points)
        equity = data.get('estimated_equity', 0)
        if equity < 0:
            score += 20
        elif equity < 10000:
            score += 10
            
        return min(score, 100)
    
    def _score_time_pressure(self, data: Dict) -> float:
        """Score time pressure indicators"""
        score = 0
        
        # Life events (40 points)
        life_events = data.get('life_events', [])
        if 'divorce' in life_events or 'death' in life_events:
            score += 40
        elif 'relocation' in life_events or 'job_loss' in life_events:
            score += 30
            
        # Property vacant (30 points)
        if data.get('occupancy_status') == 'Vacant':
            score += 30
            
        # Listing status (30 points)
        days_on_market = data.get('days_on_market', 0)
        price_reductions = data.get('price_reductions', 0)
        
        if days_on_market > 90 and price_reductions > 1:
            score += 30
        elif days_on_market > 60 or price_reductions > 0:
            score += 20
            
        return min(score, 100)
    
    def _score_property_condition(self, data: Dict) -> float:
        """Score property condition"""
        score = 100  # Start at 100 and deduct
        
        # Major systems (40 points)
        systems = data.get('systems', {})
        if systems.get('roof') == 'Poor':
            score -= 15
        if systems.get('hvac') == 'Poor':
            score -= 10
        if systems.get('plumbing') == 'Poor':
            score -= 8
        if systems.get('electrical') == 'Poor':
            score -= 7
            
        # Structural issues (30 points)
        structural = data.get('structural_issues', [])
        if 'foundation' in structural:
            score -= 20
        if 'load_bearing_walls' in structural:
            score -= 10
            
        # Cosmetic issues (20 points)
        cosmetic = data.get('cosmetic_issues', [])
        if len(cosmetic) >= 5:
            score -= 20
        elif len(cosmetic) >= 3:
            score -= 10
            
        # Property age (10 points)
        year_built = data.get('year_built', 0)
        if year_built:
            age = datetime.now().year - year_built
            if age >= 50:
                score -= 10
            elif age >= 30:
                score -= 5
                
        return max(score, 0)
    
    def _score_market_position(self, data: Dict) -> float:
        """Score market position"""
        score = 0
        
        # Market trends (30 points)
        if data.get('market_trend') == 'growing':
            score += 30
        elif data.get('market_trend') == 'stable':
            score += 20
            
        # Days on market vs average (25 points)
        dom = data.get('days_on_market', 0)
        avg_dom = data.get('market_dom', 30)
        if dom > avg_dom * 2:
            score += 25
        elif dom > avg_dom * 1.5:
            score += 15
            
        # Price per sqft vs market (25 points)
        price_psf = data.get('price_per_sqft', 0)
        market_psf = data.get('median_ppsf', 0)
        if price_psf and market_psf:
            if price_psf <= market_psf * 0.8:
                score += 25
            elif price_psf <= market_psf * 0.9:
                score += 15
                
        # Neighborhood quality (20 points)
        neighborhood_score = data.get('neighborhood_score', 0)
        if neighborhood_score >= 80:
            score += 20
        elif neighborhood_score >= 60:
            score += 15
        elif neighborhood_score >= 40:
            score += 10
            
        return min(score, 100)
    
    def _get_lead_status(self, score: float) -> str:
        """Get lead status based on score"""
        if score >= 80:
            return "Hot"
        elif score >= 60:
            return "Warm"
        return "Cold"
    
    def _get_recommended_actions(self, data: Dict, score: float) -> List[Dict]:
        """Get recommended actions based on score and data"""
        actions = []
        
        if score >= 80:
            actions.append({
                'priority': 1,
                'action': "Immediate contact",
                'reason': "High-priority lead",
                'method': "Phone"
            })
            
            if data.get('foreclosure_status') or data.get('tax_delinquent'):
                actions.append({
                    'priority': 2,
                    'action': "Submit offer",
                    'reason': "High financial distress",
                    'method': "Direct mail + Phone"
                })
                
        elif score >= 60:
            actions.append({
                'priority': 1,
                'action': "Research ownership",
                'reason': "Potential opportunity",
                'method': "Property records"
            })
            
            if data.get('occupancy_status') == 'Vacant':
                actions.append({
                    'priority': 2,
                    'action': "Drive by property",
                    'reason': "Verify vacancy",
                    'method': "In person"
                })
                
        else:
            actions.append({
                'priority': 1,
                'action': "Monitor property",
                'reason': "Low current potential",
                'method': "Add to watchlist"
            })
            
        return actions
