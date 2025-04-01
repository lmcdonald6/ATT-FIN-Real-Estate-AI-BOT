from typing import Dict, List
import logging
from datetime import datetime

class ResponseFormatter:
    """Unified response formatting system"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def format_property_analysis(self, analysis: Dict, deal_score: Dict) -> Dict:
        """Format property analysis response"""
        try:
            return {
                'property_value': self._format_value_data(analysis['property_value']),
                'property_details': self._format_property_details(analysis['property_details']),
                'tax_assessment': self._format_tax_data(analysis['tax_assessment']),
                'owner_info': self._format_owner_data(analysis['owner_info']),
                'occupancy': self._format_occupancy_data(analysis['occupancy']),
                'distress_indicators': self._format_distress_data(analysis['distress_indicators']),
                'deal_score': self._format_deal_score(deal_score),
                'key_metrics': self._format_key_metrics(analysis['investment_metrics'])
            }
        except Exception as e:
            self.logger.error(f"Error formatting property analysis: {str(e)}")
            raise
    
    def format_market_analysis(self, analysis: Dict) -> Dict:
        """Format market analysis response"""
        try:
            return {
                'price_trends': self._format_price_trends(analysis['price_trends']),
                'sales_metrics': self._format_sales_metrics(analysis['sales_metrics']),
                'market_health': self._format_market_health(analysis['market_health'])
            }
        except Exception as e:
            self.logger.error(f"Error formatting market analysis: {str(e)}")
            raise
    
    def format_lead_score(self, score_data: Dict) -> Dict:
        """Format lead scoring response"""
        try:
            return {
                'total_score': f"{score_data['total_score']}/100",
                'components': {
                    'financial_distress': f"{score_data['components']['financial_distress']}/100",
                    'time_pressure': f"{score_data['components']['time_pressure']}/100",
                    'property_condition': f"{score_data['components']['property_condition']}/100",
                    'market_position': f"{score_data['components']['market_position']}/100"
                },
                'status': score_data['status'],
                'recommended_action': score_data['recommended_actions']
            }
        except Exception as e:
            self.logger.error(f"Error formatting lead score: {str(e)}")
            raise
    
    def format_investment_analysis(self, analysis: Dict) -> Dict:
        """Format investment analysis response"""
        try:
            return {
                'arv_analysis': self._format_arv_data(analysis['arv_analysis']),
                'repair_estimate': self._format_repair_data(analysis['repair_estimate']),
                'deal_metrics': self._format_deal_metrics(analysis['deal_metrics'])
            }
        except Exception as e:
            self.logger.error(f"Error formatting investment analysis: {str(e)}")
            raise
    
    def _format_value_data(self, data: Dict) -> Dict:
        """Format property value data"""
        return {
            'estimated_value': self._format_currency(data['estimated_value']),
            'confidence_score': data['confidence_score'],
            'price_trend': data['price_trend'],
            'equity_position': (
                self._format_currency(data['equity_position'])
                if isinstance(data['equity_position'], (int, float))
                else data['equity_position']
            )
        }
    
    def _format_property_details(self, data: Dict) -> Dict:
        """Format property details"""
        return {
            'basic_info': {
                'beds': data['basic_info']['beds'],
                'baths': data['basic_info']['baths'],
                'sqft': self._format_number(data['basic_info']['sqft']),
                'year_built': data['basic_info']['year_built']
            },
            'construction': data['construction']
        }
    
    def _format_tax_data(self, data: Dict) -> Dict:
        """Format tax assessment data"""
        return {
            'current_value': self._format_currency(data['current_value']),
            'market_comparison': data['market_comparison'],
            'tax_history': [
                {
                    'year': item['year'],
                    'amount': self._format_currency(item['amount'])
                }
                for item in data['tax_history']
            ],
            'status': data['status']
        }
    
    def _format_owner_data(self, data: Dict) -> Dict:
        """Format owner information"""
        return {
            'current_owner': data['current_owner'],
            'ownership_length': data['ownership_length'],
            'portfolio_size': data['portfolio_size'],
            'estimated_equity': (
                self._format_currency(data['estimated_equity'])
                if isinstance(data['estimated_equity'], (int, float))
                else data['estimated_equity']
            )
        }
    
    def _format_occupancy_data(self, data: Dict) -> Dict:
        """Format occupancy data"""
        return {
            'status': data['status'],
            'vacancy_risk': data['vacancy_risk'],
            'utility_status': data['utility_status'],
            'mail_status': data['mail_status']
        }
    
    def _format_distress_data(self, data: Dict) -> Dict:
        """Format distress indicators"""
        return {
            'foreclosure_status': {
                'status': data['foreclosure_status']['status'],
                'stage': data['foreclosure_status']['stage'],
                'auction_date': data['foreclosure_status']['auction_date'],
                'default_amount': (
                    self._format_currency(data['foreclosure_status']['default_amount'])
                    if isinstance(data['foreclosure_status']['default_amount'], (int, float))
                    else data['foreclosure_status']['default_amount']
                )
            },
            'liens_bankruptcy': {
                'total_liens': data['liens_bankruptcy']['total_liens'],
                'lien_amount': (
                    self._format_currency(data['liens_bankruptcy']['lien_amount'])
                    if isinstance(data['liens_bankruptcy']['lien_amount'], (int, float))
                    else data['liens_bankruptcy']['lien_amount']
                ),
                'bankruptcy_status': data['liens_bankruptcy']['bankruptcy_status'],
                'risk_level': data['liens_bankruptcy']['risk_level']
            }
        }
    
    def _format_deal_score(self, data: Dict) -> Dict:
        """Format deal scoring data"""
        return {
            'total_score': f"{data['total_score']}/100",
            'components': {
                'financial_analysis': f"{data['components']['financial_analysis']}/100",
                'property_condition': f"{data['components']['property_condition']}/100",
                'market_position': f"{data['components']['market_position']}/100",
                'exit_strategy': f"{data['components']['exit_strategy']}/100"
            },
            'deal_status': data['deal_status'],
            'key_metrics': data['key_metrics']
        }
    
    def _format_key_metrics(self, data: Dict) -> Dict:
        """Format key investment metrics"""
        return {
            'purchase_metrics': {
                'price_per_sqft': self._format_currency(data['purchase_metrics']['price_per_sqft']),
                'price_to_arv_ratio': data['purchase_metrics']['price_to_arv_ratio'],
                'repair_ratio': data['purchase_metrics']['repair_ratio']
            },
            'rental_metrics': {
                'gross_rent_multiplier': data['rental_metrics']['gross_rent_multiplier'],
                'cap_rate': data['rental_metrics']['cap_rate'],
                'cash_on_cash_return': data['rental_metrics']['cash_on_cash_return']
            },
            'flip_metrics': {
                'potential_profit': self._format_currency(data['flip_metrics']['potential_profit']),
                'roi': data['flip_metrics']['roi'],
                'max_allowable_offer': self._format_currency(data['flip_metrics']['max_allowable_offer'])
            }
        }
    
    def _format_price_trends(self, data: Dict) -> Dict:
        """Format price trend data"""
        return {
            'median_price': self._format_currency(data['median_price']),
            'price_change': data['price_change'],
            'forecast_12m': data['forecast_12m']
        }
    
    def _format_sales_metrics(self, data: Dict) -> Dict:
        """Format sales metrics"""
        return {
            'monthly_sales': data['monthly_sales'],
            'days_on_market': data['days_on_market'],
            'absorption_rate': data['absorption_rate']
        }
    
    def _format_market_health(self, data: Dict) -> Dict:
        """Format market health data"""
        return {
            'inventory_months': round(data['inventory_months'], 1),
            'price_reductions': data['price_reductions'],
            'market_condition': data['market_condition']
        }
    
    def _format_arv_data(self, data: Dict) -> Dict:
        """Format ARV analysis data"""
        return {
            'estimated_arv': self._format_currency(data['estimated_arv']),
            'confidence_score': data['confidence_score'],
            'comp_count': data['comp_count'],
            'best_comps': [
                {
                    'address': comp['address'],
                    'similarity': comp['similarity'],
                    'price': self._format_currency(comp['price'])
                }
                for comp in data['best_comps']
            ]
        }
    
    def _format_repair_data(self, data: Dict) -> Dict:
        """Format repair estimate data"""
        return {
            'total_cost': self._format_currency(data['total_cost']),
            'major_items': data['major_items'],
            'contingency': (
                self._format_currency(data['contingency'])
                if isinstance(data['contingency'], (int, float))
                else data['contingency']
            )
        }
    
    def _format_deal_metrics(self, data: Dict) -> Dict:
        """Format deal metrics"""
        return {
            'mao': (
                self._format_currency(data['mao'])
                if isinstance(data['mao'], (int, float))
                else data['mao']
            ),
            'potential_profit': (
                self._format_currency(data['potential_profit'])
                if isinstance(data['potential_profit'], (int, float))
                else data['potential_profit']
            ),
            'roi': (
                f"{data['roi']:.1f}%"
                if isinstance(data['roi'], (int, float))
                else data['roi']
            ),
            'deal_score': data['deal_score']
        }
    
    def _format_currency(self, value: float) -> str:
        """Format currency values"""
        if not isinstance(value, (int, float)):
            return str(value)
        return f"${value:,.2f}"
    
    def _format_number(self, value: float) -> str:
        """Format numeric values with commas"""
        if not isinstance(value, (int, float)):
            return str(value)
        return f"{value:,}"
    
    def format_search_results(self, response: Dict) -> Dict:
        """Format property search results with analysis"""
        try:
            properties = response.get('properties', [])
            market_data = response.get('market_data', {})
            
            formatted_response = {
                'summary': {
                    'total_properties': len(properties),
                    'market_overview': self._format_market_overview(market_data),
                    'query_criteria': self._format_query_criteria(response.get('query_params', {})),
                    'timestamp': response.get('timestamp')
                },
                'properties': []
            }
            
            for prop in properties:
                formatted_response['properties'].append(
                    self._format_property_result(prop)
                )
            
            return formatted_response
            
        except Exception as e:
            self.logger.error(f"Error formatting search results: {str(e)}")
            raise
    
    def _format_market_overview(self, market_data: Dict) -> Dict:
        """Format market overview data"""
        return {
            'median_price': self._format_currency(market_data.get('median_price', 0)),
            'price_trend': market_data.get('price_trend', 'N/A'),
            'average_dom': market_data.get('average_dom', 'N/A'),
            'inventory_level': market_data.get('inventory_level', 'N/A'),
            'market_health': self._format_market_health(market_data.get('market_health', {})),
            'distressed_property_ratio': market_data.get('distressed_property_ratio', 'N/A')
        }
    
    def _format_query_criteria(self, params: Dict) -> Dict:
        """Format query parameters"""
        return {
            'location': f"{params.get('city', 'N/A')}, {params.get('state', 'N/A')} {params.get('zipcode', 'N/A')}",
            'filters': {
                'days_on_market': f">{params.get('min_days_on_market', 0)} days",
                'equity_percentage': f"≥{params.get('min_equity_percentage', 0)}%",
                'owner_type': params.get('owner_type', 'N/A'),
                'property_status': params.get('property_status', 'N/A')
            }
        }
    
    def _format_property_result(self, prop_data: Dict) -> Dict:
        """Format individual property result"""
        property_info = prop_data.get('property', {})
        analysis = prop_data.get('analysis', {})
        
        return {
            'property_details': {
                'address': property_info.get('address', 'N/A'),
                'beds': property_info.get('beds', 'N/A'),
                'baths': property_info.get('baths', 'N/A'),
                'sqft': self._format_number(property_info.get('sqft', 0)),
                'year_built': property_info.get('year_built', 'N/A'),
                'property_type': property_info.get('property_type', 'N/A')
            },
            'market_metrics': {
                'current_price': self._format_currency(analysis.get('current_price', 0)),
                'estimated_value': self._format_currency(analysis.get('estimated_value', 0)),
                'equity_percentage': f"{analysis.get('equity_percentage', 0)}%",
                'days_on_market': analysis.get('days_on_market', 'N/A')
            },
            'owner_info': self._format_owner_data(analysis.get('owner_info', {})),
            'distress_indicators': self._format_distress_data(analysis.get('distress_indicators', {})),
            'investment_potential': {
                'max_offer': self._format_currency(analysis.get('max_offer', 0)),
                'estimated_repairs': self._format_currency(analysis.get('repair_estimate', 0)),
                'potential_profit': self._format_currency(analysis.get('potential_profit', 0)),
                'roi': f"{analysis.get('roi', 0)}%"
            },
            'lead_score': self._format_lead_score(analysis.get('lead_score', {})),
            'recommended_actions': analysis.get('recommended_actions', [])
        }
    
    def format_property_analysis(self, analysis: Dict) -> Dict:
        """Format property analysis response"""
        try:
            return {
                'property_value': self._format_value_data(analysis['analysis'].get('property_value', {})),
                'property_details': self._format_property_details(analysis['analysis'].get('property_details', {})),
                'tax_assessment': self._format_tax_data(analysis['analysis'].get('tax_assessment', {})),
                'owner_info': self._format_owner_data(analysis['analysis'].get('owner_info', {})),
                'occupancy': self._format_occupancy_data(analysis['analysis'].get('occupancy', {})),
                'distress_indicators': self._format_distress_data(analysis['analysis'].get('distress_indicators', {})),
                'deal_score': analysis.get('deal_score', {}),
                'lead_score': analysis.get('lead_score', {}),
                'recommendations': analysis.get('recommendations', [])
            }
        except Exception as e:
            self.logger.error(f"Error formatting property analysis: {str(e)}")
            raise
    
    def format_market_analysis(self, analysis: Dict) -> Dict:
        """Format market analysis response"""
        try:
            return {
                'price_trends': self._format_price_trends(analysis.get('price_trends', {})),
                'sales_metrics': self._format_sales_metrics(analysis.get('sales_metrics', {})),
                'market_health': self._format_market_health(analysis.get('market_health', {})),
                'development_plans': analysis.get('development_plans', {})
            }
        except Exception as e:
            self.logger.error(f"Error formatting market analysis: {str(e)}")
            raise
    
    def format_lead_score(self, score_data: Dict) -> Dict:
        """Format lead scoring response"""
        try:
            return {
                'total_score': f"{score_data.get('total_score', 0)}/100",
                'status': score_data.get('status', 'N/A'),
                'components': {
                    'financial_distress': f"{score_data.get('components', {}).get('financial_distress', 0)}/100",
                    'time_pressure': f"{score_data.get('components', {}).get('time_pressure', 0)}/100",
                    'property_condition': f"{score_data.get('components', {}).get('property_condition', 0)}/100",
                    'market_position': f"{score_data.get('components', {}).get('market_position', 0)}/100"
                },
                'recommended_actions': score_data.get('recommended_actions', [])
            }
        except Exception as e:
            self.logger.error(f"Error formatting lead score: {str(e)}")
            raise
    
    def format_investment_analysis(self, analysis: Dict) -> Dict:
        """Format investment analysis response"""
        try:
            return {
                'arv_analysis': self._format_arv_data(analysis.get('arv_analysis', {})),
                'repair_estimate': self._format_repair_data(analysis.get('repair_estimate', {})),
                'deal_metrics': self._format_deal_metrics(analysis.get('deal_metrics', {})),
                'exit_strategy': analysis.get('exit_strategy', {}),
                'market_timing': analysis.get('market_timing', {})
            }
        except Exception as e:
            self.logger.error(f"Error formatting investment analysis: {str(e)}")
            raise
    
    def _format_value_data(self, data: Dict) -> Dict:
        """Format property value data"""
        return {
            'estimated_value': self._format_currency(data.get('estimated_value', 0)),
            'confidence_score': data.get('confidence_score', 'N/A'),
            'price_trend': data.get('price_trend', 'N/A'),
            'equity_position': self._format_currency(data.get('equity_position', 0))
        }
    
    def _format_property_details(self, data: Dict) -> Dict:
        """Format property details"""
        basic_info = data.get('basic_info', {})
        return {
            'basic_info': {
                'beds': basic_info.get('beds', 'N/A'),
                'baths': basic_info.get('baths', 'N/A'),
                'sqft': self._format_number(basic_info.get('sqft', 0)),
                'year_built': basic_info.get('year_built', 'N/A')
            },
            'construction': data.get('construction', {})
        }
    
    def _format_tax_data(self, data: Dict) -> Dict:
        """Format tax assessment data"""
        return {
            'current_value': self._format_currency(data.get('current_value', 0)),
            'market_comparison': data.get('market_comparison', 'N/A'),
            'tax_history': [
                {
                    'year': item.get('year', 'N/A'),
                    'amount': self._format_currency(item.get('amount', 0))
                }
                for item in data.get('tax_history', [])
            ],
            'status': data.get('status', 'N/A')
        }
    
    def _format_owner_data(self, data: Dict) -> Dict:
        """Format owner information"""
        return {
            'owner_type': data.get('owner_type', 'N/A'),
            'ownership_length': data.get('ownership_length', 'N/A'),
            'mailing_address': data.get('mailing_address', 'N/A'),
            'portfolio_size': data.get('portfolio_size', 'N/A'),
            'estimated_equity': self._format_currency(data.get('estimated_equity', 0))
        }
    
    def _format_currency(self, value: float) -> str:
        """Format currency values"""
        try:
            return f"${value:,.2f}" if value else "N/A"
        except:
            return "N/A"
    
    def _format_number(self, value: float) -> str:
        """Format numeric values"""
        try:
            return f"{value:,}" if value else "N/A"
        except:
            return "N/A"
