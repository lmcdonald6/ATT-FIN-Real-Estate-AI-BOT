"""Data Prioritization System for Real Estate AI Bot"""
from typing import Dict, List, Optional
from datetime import datetime, timedelta

class DataPrioritizer:
    """Prioritizes data sources and calculates lead scores"""
    
    def __init__(self):
        self.redfin_fields = {
            'price', 'beds', 'baths', 'sqft', 'year_built',
            'days_on_market', 'condition_score', 'price_history',
            'maintenance_needed', 'market_trend', 'overpriced_vs_comps'
        }
        
        self.attom_fields = {
            'tax_delinquent', 'foreclosure_status', 'liens',
            'avm_value', 'owner_name', 'mailing_address',
            'length_of_residence', 'assessed_value', 'tax_history'
        }
        
        self.refresh_rules = {
            'high_frequency': {
                'days': 1,
                'source_priority': ['redfin', 'attom']
            },
            'medium_frequency': {
                'days': 7,
                'source_priority': ['cache', 'redfin', 'attom']
            },
            'low_frequency': {
                'days': 30,
                'source_priority': ['cache', 'redfin', 'attom']
            },
            'very_low_frequency': {
                'days': 90,
                'source_priority': ['cache', 'attom']
            }
        }
    
    def get_data_source(self, field: str) -> str:
        """Determine best data source for a field"""
        if field in self.redfin_fields:
            return 'redfin'
        elif field in self.attom_fields:
            return 'attom'
        return 'unknown'
    
    def calculate_lead_score(self, data: Dict) -> Dict:
        """Calculate comprehensive lead score"""
        # Financial Distress Score (0-100)
        financial_score = self._calculate_financial_distress(data)
        
        # Time Pressure Score (0-100)
        time_score = self._calculate_time_pressure(data)
        
        # Property Condition Score (0-100)
        condition_score = self._calculate_property_condition(data)
        
        # Market Position Score (0-100)
        market_score = self._calculate_market_position(data)
        
        # Calculate total score (weighted average)
        total_score = (
            financial_score * 0.35 +  # Higher weight on financial distress
            time_score * 0.25 +
            condition_score * 0.20 +
            market_score * 0.20
        )
        
        # Determine lead status
        status = self._determine_lead_status(total_score)
        
        # Get recommended actions
        actions = self._get_recommended_actions(data, total_score)
        
        # Track data sources used
        data_sources = {
            'redfin_used': [f for f in data.keys() if f in self.redfin_fields],
            'attom_used': [f for f in data.keys() if f in self.attom_fields]
        }
        
        return {
            'total_score': total_score,
            'components': {
                'financial_distress': financial_score,
                'time_pressure': time_score,
                'property_condition': condition_score,
                'market_position': market_score
            },
            'status': status,
            'recommended_action': actions,
            'data_sources': data_sources
        }
    
    def _calculate_financial_distress(self, data: Dict) -> float:
        """Calculate financial distress score"""
        score = 0
        
        # Tax delinquency (30 points)
        if data.get('tax_delinquent'):
            score += 30
        
        # Foreclosure status (40 points)
        if data.get('foreclosure_status') == 'Pre-foreclosure':
            score += 40
        elif data.get('foreclosure_status') == 'Auction':
            score += 35
        
        # Liens present (20 points)
        if data.get('liens', False):
            score += 20
        
        # Price reductions (10 points)
        price_history = data.get('price_history', [])
        if price_history and len(price_history) >= 2:
            initial_price = price_history[0]['price']
            current_price = price_history[-1]['price']
            if current_price < initial_price:
                reduction = ((initial_price - current_price) / initial_price) * 100
                if reduction >= 10:
                    score += 10
                elif reduction >= 5:
                    score += 5
        
        return min(score, 100)  # Cap at 100
    
    def _calculate_time_pressure(self, data: Dict) -> float:
        """Calculate time pressure score"""
        score = 0
        
        # Days on market (30 points)
        dom = data.get('days_on_market', 0)
        if dom >= 90:
            score += 30
        elif dom >= 60:
            score += 20
        elif dom >= 30:
            score += 10
        
        # Foreclosure timeline (40 points)
        if data.get('foreclosure_status'):
            auction_date = data.get('auction_date')
            if auction_date:
                days_to_auction = (datetime.strptime(auction_date, '%Y-%m-%d') - datetime.now()).days
                if days_to_auction <= 30:
                    score += 40
                elif days_to_auction <= 60:
                    score += 30
                elif days_to_auction <= 90:
                    score += 20
        
        # Overpriced vs comps (30 points)
        if data.get('overpriced_vs_comps'):
            score += 30
        
        return min(score, 100)  # Cap at 100
    
    def _calculate_property_condition(self, data: Dict) -> float:
        """Calculate property condition score"""
        score = 100  # Start at 100 and deduct
        
        # Condition score from Redfin (50 points)
        condition = data.get('condition_score', 100)
        score = min(score, condition)
        
        # Maintenance needed (30 points)
        if data.get('maintenance_needed'):
            score -= 30
        
        # Major repairs needed (20 points)
        if data.get('major_repairs'):
            score -= 20
        
        return max(score, 0)  # Ensure non-negative
    
    def _calculate_market_position(self, data: Dict) -> float:
        """Calculate market position score"""
        score = 0
        
        # Market trend (40 points)
        trend = data.get('market_trend', 'stable')
        if trend == 'declining':
            score += 40
        elif trend == 'stable':
            score += 20
        
        # Price vs market (30 points)
        list_price = data.get('price', 0)
        median_price = data.get('median_price', 0)
        if list_price and median_price:
            if list_price > median_price * 1.1:  # 10% above median
                score += 30
            elif list_price > median_price * 1.05:  # 5% above median
                score += 20
        
        # Days on market vs market average (30 points)
        dom = data.get('days_on_market', 0)
        market_dom = data.get('market_dom', 30)
        if dom > market_dom * 2:
            score += 30
        elif dom > market_dom * 1.5:
            score += 20
        elif dom > market_dom:
            score += 10
        
        return min(score, 100)  # Cap at 100
    
    def _determine_lead_status(self, score: float) -> str:
        """Determine lead status based on score"""
        if score >= 80:
            return 'Hot'
        elif score >= 60:
            return 'Warm'
        return 'Cold'
    
    def _get_recommended_actions(self, data: Dict, score: float) -> List[Dict]:
        """Get recommended actions based on lead data"""
        actions = []
        
        # Immediate Contact for Hot Leads
        if score >= 80:
            actions.append({
                'priority': 1,
                'action': 'Immediate contact',
                'reason': 'High-priority lead',
                'method': 'Phone + Direct mail'
            })
        
        # Financial Distress Follow-up
        if data.get('financial_distress', 0) >= 70:
            actions.append({
                'priority': 2,
                'action': 'Submit offer',
                'reason': 'High financial distress',
                'method': 'Direct mail + Phone'
            })
        
        # Property Condition Issues
        if data.get('condition_score', 100) <= 50:
            actions.append({
                'priority': 3,
                'action': 'Schedule inspection',
                'reason': 'Poor property condition',
                'method': 'In-person visit'
            })
        
        # Overpriced Property
        if data.get('overpriced_vs_comps'):
            actions.append({
                'priority': 4,
                'action': 'Submit lower offer',
                'reason': 'Overpriced property',
                'method': 'Email + Direct mail'
            })
        
        return sorted(actions, key=lambda x: x['priority'])

    def format_property_analysis(self, data: Dict) -> Dict:
        """Format property analysis response"""
        return {
            'property_value': {
                'estimated_value': f"${data.get('avm_value', 0):,.2f}",
                'confidence_score': f"{data.get('confidence_score', 0)}%",
                'price_trend': data.get('market_trend', 'stable'),
                'equity_position': self._calculate_equity_position(data)
            },
            'property_details': {
                'basic_info': {
                    'beds': data.get('beds', 'N/A'),
                    'baths': data.get('baths', 'N/A'),
                    'sqft': f"{data.get('sqft', 0):,}",
                    'year_built': data.get('year_built', 'N/A')
                },
                'construction': {
                    'foundation': data.get('foundation_type', 'N/A'),
                    'roof': data.get('roof_type', 'N/A'),
                    'systems': data.get('systems', {})
                }
            },
            'tax_assessment': {
                'current_value': f"${data.get('assessed_value', 0):,.2f}",
                'market_comparison': self._calculate_tax_ratio(data),
                'tax_history': data.get('tax_history', []),
                'status': 'Delinquent' if data.get('tax_delinquent') else 'Current'
            }
        }
    
    def format_seller_insights(self, data: Dict) -> Dict:
        """Format seller insights response"""
        return {
            'owner_info': {
                'current_owner': data.get('owner_name', 'N/A'),
                'ownership_length': f"{data.get('length_of_residence', 0)} years",
                'portfolio_size': len(data.get('other_properties', [])),
                'estimated_equity': self._calculate_equity_position(data)
            },
            'occupancy': {
                'status': data.get('occupancy_status', 'Unknown'),
                'vacancy_risk': self._calculate_vacancy_risk(data),
                'utility_status': data.get('utility_status', 'Unknown')
            },
            'motivation': {
                'financial_pressure': data.get('financial_distress', 0),
                'time_pressure': data.get('time_pressure', 0),
                'life_events': data.get('motivation_factors', [])
            }
        }
    
    def format_distressed_property(self, data: Dict) -> Dict:
        """Format distressed property response"""
        return {
            'foreclosure_status': {
                'status': data.get('foreclosure_status', 'None'),
                'stage': data.get('foreclosure_stage', 'N/A'),
                'auction_date': data.get('auction_date', 'N/A'),
                'default_amount': f"${data.get('default_amount', 0):,.2f}"
            },
            'liens_bankruptcy': {
                'total_liens': len(data.get('liens', [])),
                'lien_amount': f"${data.get('lien_amount', 0):,.2f}",
                'bankruptcy_status': data.get('bankruptcy_status', 'None')
            },
            'timeline': self._format_distressed_timeline(data)
        }
    
    def format_market_analysis(self, data: Dict) -> Dict:
        """Format market analysis response"""
        return {
            'price_trends': {
                'median_price': f"${data.get('median_price', 0):,.2f}",
                'price_change': f"{data.get('price_change', 0)}%",
                'days_on_market': data.get('days_on_market', 0)
            },
            'sales_metrics': {
                'velocity': f"{data.get('sales_velocity', 0)} sales/month",
                'inventory': f"{data.get('inventory_months', 0)} months",
                'absorption': f"{data.get('absorption_rate', 0)}%"
            },
            'price_per_sqft': {
                'subject': f"${data.get('price_per_sqft', 0):,.2f}",
                'median': f"${data.get('median_ppsf', 0):,.2f}",
                'trend': data.get('ppsf_trend', 'stable')
            }
        }
    
    def format_investment_metrics(self, data: Dict) -> Dict:
        """Format investment metrics response"""
        return {
            'arv_analysis': {
                'estimated_arv': f"${data.get('arv', 0):,.2f}",
                'confidence_score': f"{data.get('arv_confidence', 0)}%",
                'comp_count': len(data.get('arv_comps', []))
            },
            'repair_estimate': {
                'total_cost': f"${data.get('repair_cost', 0):,.2f}",
                'major_items': data.get('major_repairs', []),
                'contingency': f"${data.get('repair_contingency', 0):,.2f}"
            },
            'deal_metrics': {
                'mao': f"${data.get('mao', 0):,.2f}",
                'potential_profit': f"${data.get('potential_profit', 0):,.2f}",
                'roi': f"{data.get('roi', 0)}%",
                'holding_costs': f"${data.get('holding_costs', 0):,.2f}/month"
            }
        }
    
    def _calculate_equity_position(self, data: Dict) -> str:
        """Calculate equity position"""
        value = data.get('avm_value', 0)
        mortgage = data.get('mortgage_amount', 0)
        if value and mortgage:
            equity_percent = ((value - mortgage) / value) * 100
            return f"{equity_percent:.1f}% equity"
        return "Unknown"
    
    def _calculate_tax_ratio(self, data: Dict) -> str:
        """Calculate tax assessed to market value ratio"""
        assessed = data.get('assessed_value', 0)
        market = data.get('avm_value', 0)
        if assessed and market:
            ratio = (assessed / market) * 100
            return f"{ratio:.1f}% of market value"
        return "Unknown"
    
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
            return "High"
        elif risk_factors == 1:
            return "Medium"
        return "Low"
    
    def _format_distressed_timeline(self, data: Dict) -> List[Dict]:
        """Format distressed property timeline"""
        timeline = []
        
        if data.get('default_date'):
            timeline.append({
                'date': data['default_date'],
                'event': 'Default',
                'amount': f"${data.get('default_amount', 0):,.2f}"
            })
            
        if data.get('nod_date'):
            timeline.append({
                'date': data['nod_date'],
                'event': 'Notice of Default',
                'status': 'Filed'
            })
            
        if data.get('auction_date'):
            timeline.append({
                'date': data['auction_date'],
                'event': 'Auction Scheduled',
                'opening_bid': f"${data.get('opening_bid', 0):,.2f}"
            })
            
        return sorted(timeline, key=lambda x: x['date'])

    def calculate_deal_score(self, data: Dict) -> Dict:
        """Calculate comprehensive deal score for real estate agents"""
        
        # 1. Financial Analysis (35% of total score)
        financial_score = self._analyze_financial_metrics(data)
        
        # 2. Property Condition (25% of total score)
        condition_score = self._analyze_property_condition(data)
        
        # 3. Market Analysis (20% of total score)
        market_score = self._analyze_market_position(data)
        
        # 4. Exit Strategy Viability (20% of total score)
        exit_score = self._analyze_exit_strategies(data)
        
        # Calculate weighted total score
        total_score = (
            financial_score * 0.35 +
            condition_score * 0.25 +
            market_score * 0.20 +
            exit_score * 0.20
        )
        
        return {
            'total_score': round(total_score),
            'components': {
                'financial_analysis': round(financial_score),
                'property_condition': round(condition_score),
                'market_position': round(market_score),
                'exit_strategy': round(exit_score)
            },
            'deal_status': self._get_deal_status(total_score),
            'recommendations': self._get_deal_recommendations(data, total_score),
            'key_metrics': self._calculate_key_metrics(data)
        }
    
    def _analyze_financial_metrics(self, data: Dict) -> float:
        """Analyze financial metrics for deal scoring"""
        score = 0
        
        # 1. Purchase Price vs ARV (40 points)
        arv = data.get('arv', 0)
        purchase_price = data.get('price', 0)
        if arv and purchase_price:
            price_to_arv = purchase_price / arv
            if price_to_arv <= 0.65:  # 65% rule
                score += 40
            elif price_to_arv <= 0.75:
                score += 30
            elif price_to_arv <= 0.85:
                score += 20
        
        # 2. Equity Position (20 points)
        market_value = data.get('avm_value', 0)
        if market_value and purchase_price:
            equity = (market_value - purchase_price) / market_value
            if equity >= 0.30:  # 30% equity
                score += 20
            elif equity >= 0.20:
                score += 15
            elif equity >= 0.10:
                score += 10
        
        # 3. Cash Flow Potential (20 points)
        rental_estimate = data.get('rental_estimate', 0)
        monthly_costs = self._calculate_monthly_costs(data)
        if rental_estimate and monthly_costs:
            cash_flow = rental_estimate - monthly_costs
            if cash_flow >= 300:  # $300/month minimum cash flow
                score += 20
            elif cash_flow >= 200:
                score += 15
            elif cash_flow >= 100:
                score += 10
        
        # 4. ROI Potential (20 points)
        total_investment = purchase_price + data.get('repair_cost', 0)
        annual_return = self._calculate_annual_return(data)
        if total_investment and annual_return:
            roi = (annual_return / total_investment) * 100
            if roi >= 20:  # 20% ROI threshold
                score += 20
            elif roi >= 15:
                score += 15
            elif roi >= 10:
                score += 10
        
        return min(score, 100)
    
    def _analyze_property_condition(self, data: Dict) -> float:
        """Analyze property condition for deal scoring"""
        score = 100  # Start at 100 and deduct
        
        # 1. Major Systems (40 points)
        systems = data.get('systems', {})
        major_deductions = {
            'roof': 15,
            'hvac': 10,
            'plumbing': 8,
            'electrical': 7
        }
        for system, deduction in major_deductions.items():
            if systems.get(system) == 'Poor':
                score -= deduction
        
        # 2. Structural Issues (30 points)
        structural = data.get('structural_issues', [])
        if 'foundation' in structural:
            score -= 20
        if 'load_bearing_walls' in structural:
            score -= 10
        
        # 3. Cosmetic Issues (20 points)
        cosmetic = data.get('cosmetic_issues', [])
        cosmetic_count = len(cosmetic)
        if cosmetic_count >= 5:
            score -= 20
        elif cosmetic_count >= 3:
            score -= 10
        
        # 4. Property Age (10 points)
        year_built = data.get('year_built', 0)
        if year_built:
            age = 2025 - year_built
            if age >= 50:
                score -= 10
            elif age >= 30:
                score -= 5
        
        return max(score, 0)
    
    def _analyze_market_position(self, data: Dict) -> float:
        """Analyze market position for deal scoring"""
        score = 0
        
        # 1. Market Trends (30 points)
        if data.get('market_trend') == 'growing':
            score += 30
        elif data.get('market_trend') == 'stable':
            score += 20
        
        # 2. Days on Market vs Average (25 points)
        dom = data.get('days_on_market', 0)
        avg_dom = data.get('market_dom', 30)
        if dom > avg_dom * 2:
            score += 25  # Property potentially undervalued
        elif dom > avg_dom * 1.5:
            score += 15
        
        # 3. Price per Sqft vs Market (25 points)
        price_psf = data.get('price_per_sqft', 0)
        market_psf = data.get('median_ppsf', 0)
        if price_psf and market_psf:
            if price_psf <= market_psf * 0.8:  # 20% below market
                score += 25
            elif price_psf <= market_psf * 0.9:
                score += 15
        
        # 4. Neighborhood Quality (20 points)
        neighborhood_score = data.get('neighborhood_score', 0)
        if neighborhood_score >= 80:
            score += 20
        elif neighborhood_score >= 60:
            score += 15
        elif neighborhood_score >= 40:
            score += 10
        
        return min(score, 100)
    
    def _analyze_exit_strategies(self, data: Dict) -> float:
        """Analyze viability of exit strategies"""
        score = 0
        
        # 1. Fix and Flip Viability (35 points)
        if self._check_flip_viability(data):
            score += 35
        
        # 2. Rental Potential (25 points)
        if self._check_rental_viability(data):
            score += 25
        
        # 3. Wholesale Potential (20 points)
        if self._check_wholesale_viability(data):
            score += 20
        
        # 4. Development Potential (20 points)
        if self._check_development_potential(data):
            score += 20
        
        return min(score, 100)
    
    def _calculate_monthly_costs(self, data: Dict) -> float:
        """Calculate total monthly costs"""
        mortgage = data.get('estimated_mortgage', 0)
        taxes = data.get('property_tax', 0) / 12
        insurance = data.get('insurance', 0) / 12
        maintenance = data.get('sqft', 0) * 0.1  # $0.10 per sqft
        vacancy = data.get('rental_estimate', 0) * 0.08  # 8% vacancy rate
        return mortgage + taxes + insurance + maintenance + vacancy
    
    def _calculate_annual_return(self, data: Dict) -> float:
        """Calculate potential annual return"""
        # Rental income
        monthly_rent = data.get('rental_estimate', 0)
        annual_rent = monthly_rent * 12
        
        # Operating expenses
        monthly_costs = self._calculate_monthly_costs(data)
        annual_costs = monthly_costs * 12
        
        # Appreciation
        purchase_price = data.get('price', 0)
        appreciation_rate = data.get('market_appreciation', 0.03)
        appreciation = purchase_price * appreciation_rate
        
        return (annual_rent - annual_costs) + appreciation
    
    def _get_deal_status(self, score: float) -> str:
        """Get deal status based on score"""
        if score >= 80:
            return "Strong Deal - Immediate Action Recommended"
        elif score >= 70:
            return "Good Deal - Worth Pursuing"
        elif score >= 60:
            return "Fair Deal - Additional Due Diligence Needed"
        return "Weak Deal - Consider Passing"
    
    def _calculate_key_metrics(self, data: Dict) -> Dict:
        """Calculate key real estate metrics"""
        purchase_price = data.get('price', 0)
        arv = data.get('arv', 0)
        repair_cost = data.get('repair_cost', 0)
        rental_estimate = data.get('rental_estimate', 0)
        
        # Calculate key metrics
        return {
            'purchase_metrics': {
                'price_per_sqft': self._calculate_price_per_sqft(data),
                'price_to_arv_ratio': f"{(purchase_price / arv * 100 if arv else 0):.1f}%",
                'repair_ratio': f"{(repair_cost / purchase_price * 100 if purchase_price else 0):.1f}%"
            },
            'rental_metrics': {
                'gross_rent_multiplier': f"{(purchase_price / (rental_estimate * 12) if rental_estimate else 0):.2f}",
                'cap_rate': f"{self._calculate_cap_rate(data):.1f}%",
                'cash_on_cash_return': f"{self._calculate_coc_return(data):.1f}%"
            },
            'flip_metrics': {
                'potential_profit': f"${(arv - purchase_price - repair_cost):,.2f}",
                'roi': f"{((arv - purchase_price - repair_cost) / (purchase_price + repair_cost) * 100 if (purchase_price + repair_cost) else 0):.1f}%",
                'max_allowable_offer': f"${self._calculate_mao(data):,.2f}"
            }
        }
    
    def _check_flip_viability(self, data: Dict) -> bool:
        """Check if property is viable for fix and flip"""
        arv = data.get('arv', 0)
        purchase_price = data.get('price', 0)
        repair_cost = data.get('repair_cost', 0)
        
        if not all([arv, purchase_price, repair_cost]):
            return False
            
        total_cost = purchase_price + repair_cost
        potential_profit = arv - total_cost
        roi = (potential_profit / total_cost) * 100
        
        return roi >= 20 and potential_profit >= 30000
    
    def _check_rental_viability(self, data: Dict) -> bool:
        """Check if property is viable for rental"""
        rental_estimate = data.get('rental_estimate', 0)
        monthly_costs = self._calculate_monthly_costs(data)
        
        if not all([rental_estimate, monthly_costs]):
            return False
            
        cash_flow = rental_estimate - monthly_costs
        cap_rate = self._calculate_cap_rate(data)
        
        return cash_flow >= 200 and cap_rate >= 8
    
    def _check_wholesale_viability(self, data: Dict) -> bool:
        """Check if property is viable for wholesaling"""
        arv = data.get('arv', 0)
        purchase_price = data.get('price', 0)
        repair_cost = data.get('repair_cost', 0)
        
        if not all([arv, purchase_price, repair_cost]):
            return False
            
        max_offer = self._calculate_mao(data)
        spread = max_offer - purchase_price
        
        return spread >= 15000
    
    def _check_development_potential(self, data: Dict) -> bool:
        """Check if property has development potential"""
        lot_size = data.get('lot_size', 0)
        zoning = data.get('zoning', '')
        
        if not lot_size:
            return False
            
        return lot_size >= 5000 and 'residential' in zoning.lower()
    
    def _calculate_price_per_sqft(self, data: Dict) -> float:
        """Calculate price per square foot"""
        price = data.get('price', 0)
        sqft = data.get('sqft', 0)
        return price / sqft if sqft else 0
    
    def _calculate_cap_rate(self, data: Dict) -> float:
        """Calculate capitalization rate"""
        noi = self._calculate_annual_return(data)
        purchase_price = data.get('price', 0)
        return (noi / purchase_price * 100) if purchase_price else 0
    
    def _calculate_coc_return(self, data: Dict) -> float:
        """Calculate cash on cash return"""
        annual_cash_flow = (data.get('rental_estimate', 0) - self._calculate_monthly_costs(data)) * 12
        down_payment = data.get('price', 0) * 0.20  # Assuming 20% down
        closing_costs = data.get('price', 0) * 0.03  # Assuming 3% closing costs
        repair_cost = data.get('repair_cost', 0)
        
        total_investment = down_payment + closing_costs + repair_cost
        return (annual_cash_flow / total_investment * 100) if total_investment else 0
    
    def _calculate_mao(self, data: Dict) -> float:
        """Calculate Maximum Allowable Offer"""
        arv = data.get('arv', 0)
        repair_cost = data.get('repair_cost', 0)
        holding_costs = data.get('holding_costs', 0)
        
        if not arv:
            return 0
            
        # 70% ARV Rule - Adjusting for repairs and holding costs
        mao = (arv * 0.70) - repair_cost - holding_costs
        return max(mao, 0)
