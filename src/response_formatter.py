"""Response Formatter for Real Estate AI Bot"""
from typing import Dict, List, Optional
from datetime import datetime

class ResponseFormatter:
    """Formats responses according to defined query patterns"""
    
    def format_property_analysis(self, data: Dict) -> Dict:
        """Format property analysis and valuation response"""
        return {
            'property_value': {
                'estimated_value': self._format_currency(data.get('avm_value')),
                'confidence_score': self._format_percentage(data.get('confidence_score')),
                'price_trend': data.get('market_trend', 'stable'),
                'equity_position': self._format_percentage(data.get('equity_position'))
            },
            'property_details': {
                'basic_info': {
                    'beds': data.get('beds', 'N/A'),
                    'baths': data.get('baths', 'N/A'),
                    'sqft': self._format_number(data.get('sqft')),
                    'year_built': data.get('year_built', 'N/A')
                },
                'construction': {
                    'foundation': data.get('foundation_type', 'N/A'),
                    'roof': data.get('roof_type', 'N/A'),
                    'systems': data.get('systems', {})
                }
            },
            'tax_assessment': {
                'current_value': self._format_currency(data.get('assessed_value')),
                'market_comparison': self._format_percentage(data.get('tax_ratio')),
                'tax_history': data.get('tax_history', []),
                'status': data.get('tax_status', 'Unknown')
            }
        }
    
    def format_seller_insights(self, data: Dict) -> Dict:
        """Format seller and ownership insights response"""
        return {
            'owner_info': {
                'current_owner': data.get('owner_name', 'N/A'),
                'ownership_length': f"{data.get('length_of_residence', 0)} years",
                'portfolio_size': data.get('portfolio_size', 0),
                'estimated_equity': self._format_currency(data.get('equity'))
            },
            'occupancy': {
                'status': data.get('occupancy_status', 'Unknown'),
                'vacancy_risk': self._calculate_vacancy_risk(data),
                'utility_status': data.get('utility_status', 'Unknown'),
                'mail_status': data.get('mail_status', 'Unknown')
            },
            'motivation': {
                'financial_pressure': self._format_score(data.get('financial_distress')),
                'time_pressure': self._format_score(data.get('time_pressure')),
                'life_events': data.get('motivation_factors', []),
                'overall_motivation': self._calculate_motivation_score(data)
            }
        }
    
    def format_distressed_property(self, data: Dict) -> Dict:
        """Format distressed property and off-market leads response"""
        return {
            'foreclosure_status': {
                'status': data.get('foreclosure_status', 'None'),
                'stage': data.get('foreclosure_stage', 'N/A'),
                'auction_date': data.get('auction_date', 'N/A'),
                'default_amount': self._format_currency(data.get('default_amount'))
            },
            'liens_bankruptcy': {
                'total_liens': data.get('total_liens', 0),
                'lien_amount': self._format_currency(data.get('lien_amount')),
                'bankruptcy_status': data.get('bankruptcy_status', 'None'),
                'risk_level': self._calculate_distress_level(data)
            },
            'contact_info': {
                'owner_name': data.get('owner_name', 'N/A'),
                'mailing_address': data.get('mailing_address', 'N/A'),
                'phone': data.get('phone', 'N/A'),
                'best_contact': self._determine_best_contact(data)
            }
        }
    
    def format_market_analysis(self, data: Dict) -> Dict:
        """Format neighborhood and market trends response"""
        return {
            'price_trends': {
                'median_price': self._format_currency(data.get('median_price')),
                'price_change': self._format_percentage(data.get('price_change')),
                'forecast_12m': self._format_percentage(data.get('price_forecast'))
            },
            'sales_metrics': {
                'monthly_sales': data.get('monthly_sales', 0),
                'days_on_market': data.get('days_on_market', 0),
                'absorption_rate': self._format_percentage(data.get('absorption_rate'))
            },
            'market_health': {
                'inventory_months': data.get('inventory_months', 0),
                'price_reductions': self._format_percentage(data.get('price_reduced_ratio')),
                'market_condition': self._determine_market_condition(data)
            }
        }
    
    def format_investment_analysis(self, data: Dict) -> Dict:
        """Format investment and wholesale strategy response"""
        return {
            'arv_analysis': {
                'estimated_arv': self._format_currency(data.get('arv')),
                'confidence_score': self._format_percentage(data.get('arv_confidence')),
                'comp_count': len(data.get('arv_comps', [])),
                'best_comps': self._format_top_comps(data.get('arv_comps', []))
            },
            'repair_estimate': {
                'total_cost': self._format_currency(data.get('repair_cost')),
                'major_items': data.get('major_repairs', []),
                'contingency': self._format_currency(data.get('repair_contingency'))
            },
            'deal_metrics': {
                'mao': self._format_currency(data.get('mao')),
                'potential_profit': self._format_currency(data.get('potential_profit')),
                'roi': self._format_percentage(data.get('roi')),
                'deal_score': self._calculate_deal_score(data)
            }
        }
    
    def format_lead_score(self, data: Dict) -> Dict:
        """Format lead scoring response"""
        return {
            'total_score': self._format_score(data.get('total_score')),
            'components': {
                'financial_distress': self._format_score(data.get('financial_distress')),
                'time_pressure': self._format_score(data.get('time_pressure')),
                'property_condition': self._format_score(data.get('property_condition')),
                'market_position': self._format_score(data.get('market_position'))
            },
            'status': self._determine_lead_status(data.get('total_score', 0)),
            'recommended_action': self._get_recommended_actions(data)
        }
    
    def _format_currency(self, value: Optional[float]) -> str:
        """Format currency values"""
        if value is None:
            return 'N/A'
        return f"${value:,.2f}"
    
    def _format_percentage(self, value: Optional[float]) -> str:
        """Format percentage values"""
        if value is None:
            return 'N/A'
        return f"{value:.1f}%"
    
    def _format_number(self, value: Optional[int]) -> str:
        """Format numeric values"""
        if value is None:
            return 'N/A'
        return f"{value:,}"
    
    def _format_score(self, value: Optional[float]) -> str:
        """Format score values (0-100)"""
        if value is None:
            return 'N/A'
        return f"{value:.0f}/100"
    
    def _calculate_vacancy_risk(self, data: Dict) -> str:
        """Calculate vacancy risk level"""
        risk_factors = 0
        if data.get('utility_status') == 'Inactive':
            risk_factors += 1
        if data.get('mail_status') == 'Return to Sender':
            risk_factors += 1
        if data.get('occupancy_status') == 'Unknown':
            risk_factors += 1
        
        if risk_factors >= 2:
            return 'High'
        elif risk_factors == 1:
            return 'Medium'
        return 'Low'
    
    def _calculate_motivation_score(self, data: Dict) -> int:
        """Calculate overall motivation score"""
        financial = data.get('financial_distress', 0)
        time = data.get('time_pressure', 0)
        return int((financial + time) / 2)
    
    def _calculate_distress_level(self, data: Dict) -> str:
        """Calculate property distress level"""
        factors = 0
        if data.get('foreclosure_status') != 'None':
            factors += 2
        if data.get('tax_delinquent'):
            factors += 1
        if data.get('total_liens', 0) > 0:
            factors += 1
            
        if factors >= 3:
            return 'High'
        elif factors >= 1:
            return 'Medium'
        return 'Low'
    
    def _determine_best_contact(self, data: Dict) -> str:
        """Determine best contact method"""
        if data.get('phone'):
            return 'Phone'
        elif data.get('mailing_address') and data.get('occupancy_status') == 'Owner Occupied':
            return 'Direct Mail'
        return 'Skip Trace Required'
    
    def _determine_market_condition(self, data: Dict) -> str:
        """Determine market condition"""
        months = data.get('inventory_months', 6)
        if months < 3:
            return "Seller's Market"
        elif months > 6:
            return "Buyer's Market"
        return 'Balanced Market'
    
    def _format_top_comps(self, comps: List[Dict], limit: int = 3) -> List[Dict]:
        """Format top comparable properties"""
        return sorted(comps, key=lambda x: x.get('similarity', 0), reverse=True)[:limit]
    
    def _calculate_deal_score(self, data: Dict) -> int:
        """Calculate overall deal score"""
        arv = data.get('arv', 0)
        purchase = data.get('mao', 0)
        repairs = data.get('repair_cost', 0)
        
        if not all([arv, purchase, repairs]):
            return 0
            
        potential_profit = arv - (purchase + repairs)
        roi = (potential_profit / (purchase + repairs)) * 100
        
        if roi >= 30:
            return 100
        elif roi >= 20:
            return 75
        elif roi >= 15:
            return 50
        return 25
    
    def _determine_lead_status(self, score: float) -> str:
        """Determine lead status based on score"""
        if score >= 80:
            return 'Hot'
        elif score >= 60:
            return 'Warm'
        return 'Cold'
    
    def _get_recommended_actions(self, data: Dict) -> List[Dict]:
        """Get recommended actions based on lead data"""
        score = data.get('total_score', 0)
        actions = []
        
        if score >= 80:
            actions.append({
                'priority': 1,
                'action': 'Immediate contact',
                'reason': 'High-priority lead',
                'method': self._determine_best_contact(data)
            })
        
        if data.get('financial_distress', 0) >= 70:
            actions.append({
                'priority': 2,
                'action': 'Submit offer',
                'reason': 'High financial distress',
                'method': 'Direct mail + Phone'
            })
            
        if data.get('property_condition', 0) <= 50:
            actions.append({
                'priority': 3,
                'action': 'Schedule inspection',
                'reason': 'Poor property condition',
                'method': 'In-person visit'
            })
        
        return sorted(actions, key=lambda x: x['priority'])
