"""
ATTOM Data Extractors
Specialized extractors for each ATTOM API endpoint
"""
from typing import Dict, List, Optional
from datetime import datetime
import json
import logging

class AttomDataExtractor:
    """Extract and structure data from ATTOM API responses"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def search_properties(self, city: str, state: str, zipcode: str) -> List[Dict]:
        """Search for properties matching specified criteria"""
        try:
            # Simulated property data for testing
            properties = [
                {
                    'address': '123 Oak Street',
                    'city': city,
                    'state': state,
                    'zipcode': zipcode,
                    'property_type': 'Single Family',
                    'beds': 3,
                    'baths': 2,
                    'sqft': 1500,
                    'year_built': 1985,
                    'lot_size': 0.25
                },
                {
                    'address': '456 Pine Avenue',
                    'city': city,
                    'state': state,
                    'zipcode': zipcode,
                    'property_type': 'Single Family',
                    'beds': 4,
                    'baths': 3,
                    'sqft': 2200,
                    'year_built': 1990,
                    'lot_size': 0.3
                },
                {
                    'address': '789 Maple Drive',
                    'city': city,
                    'state': state,
                    'zipcode': zipcode,
                    'property_type': 'Single Family',
                    'beds': 3,
                    'baths': 2,
                    'sqft': 1800,
                    'year_built': 1988,
                    'lot_size': 0.28
                }
            ]
            
            return properties
            
        except Exception as e:
            self.logger.error(f"Error searching properties: {str(e)}")
            raise
    
    def extract_property_details(self, response: Dict) -> Dict:
        """Extract comprehensive property details"""
        try:
            property_data = response.get('property', {})
            return {
                'address': self._extract_address(property_data),
                'basic_info': self._extract_basic_info(property_data),
                'construction': self._extract_construction(property_data),
                'systems': self._extract_systems(property_data),
                'features': self._extract_features(property_data),
                'lot': self._extract_lot_info(property_data),
                'source': 'ATTOM',
                'last_updated': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error extracting property details: {str(e)}")
            raise
    
    def extract_tax_assessment(self, response: Dict) -> Dict:
        """Extract tax assessment data"""
        try:
            tax_data = response.get('assessment', {})
            return {
                'address': self._extract_address(response),
                'current_value': self._extract_tax_value(tax_data),
                'tax_year': tax_data.get('tax_year'),
                'tax_amount': tax_data.get('tax_amount'),
                'market_value': tax_data.get('market_value'),
                'assessment_history': self._extract_tax_history(tax_data),
                'exemptions': self._extract_exemptions(tax_data),
                'last_updated': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error extracting tax assessment: {str(e)}")
            raise
    
    def extract_valuation(self, response: Dict) -> Dict:
        """Extract property valuation data"""
        try:
            value_data = response.get('value', {})
            return {
                'address': self._extract_address(response),
                'estimated_value': value_data.get('amount'),
                'confidence_score': value_data.get('confidence'),
                'value_range': {
                    'low': value_data.get('range_low'),
                    'high': value_data.get('range_high')
                },
                'historical_values': self._extract_historical_values(value_data),
                'comps': self._extract_comps(value_data),
                'last_updated': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error extracting valuation: {str(e)}")
            raise
    
    def extract_owner_info(self, response: Dict) -> Dict:
        """Extract owner information"""
        try:
            owner_data = response.get('owner', {})
            return {
                'address': self._extract_address(response),
                'current_owner': self._extract_current_owner(owner_data),
                'ownership_history': self._extract_ownership_history(owner_data),
                'portfolio': self._extract_portfolio(owner_data),
                'contact_info': self._extract_contact_info(owner_data),
                'last_updated': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error extracting owner info: {str(e)}")
            raise
    
    def extract_market_data(self, response: Dict) -> Dict:
        """Extract market analysis data"""
        try:
            market_data = response.get('market', {})
            return {
                'zipcode': response.get('zipcode', ''),
                'price_trends': self._extract_price_trends(market_data),
                'sales_metrics': self._extract_sales_metrics(market_data),
                'inventory': self._extract_inventory(market_data),
                'rental_metrics': self._extract_rental_metrics(market_data),
                'last_updated': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error extracting market data: {str(e)}")
            raise
    
    def extract_foreclosure(self, response: Dict) -> Dict:
        """Extract foreclosure and distressed property data"""
        try:
            foreclosure_data = response.get('foreclosure', {})
            return {
                'address': self._extract_address(response),
                'status': foreclosure_data.get('status'),
                'stage': foreclosure_data.get('stage'),
                'auction_info': self._extract_auction_info(foreclosure_data),
                'default_info': self._extract_default_info(foreclosure_data),
                'timeline': self._extract_foreclosure_timeline(foreclosure_data),
                'last_updated': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error extracting foreclosure data: {str(e)}")
            raise
    
    def extract_deed(self, response: Dict) -> Dict:
        """Extract deed and transaction history"""
        try:
            deed_data = response.get('deed', {})
            return {
                'address': self._extract_address(response),
                'current_deed': self._extract_current_deed(deed_data),
                'transaction_history': self._extract_transactions(deed_data),
                'mortgage_info': self._extract_mortgage_info(deed_data),
                'last_updated': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error extracting deed data: {str(e)}")
            raise
    
    def extract_mls(self, response: Dict) -> Dict:
        """Extract MLS listing history"""
        try:
            mls_data = response.get('mls', {})
            return {
                'address': self._extract_address(response),
                'current_listing': self._extract_current_listing(mls_data),
                'listing_history': self._extract_listing_history(mls_data),
                'price_changes': self._extract_price_changes(mls_data),
                'days_on_market': mls_data.get('days_on_market'),
                'last_updated': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error extracting MLS data: {str(e)}")
            raise
    
    def extract_zoning(self, response: Dict) -> Dict:
        """Extract zoning and land use data"""
        try:
            zoning_data = response.get('zoning', {})
            return {
                'address': self._extract_address(response),
                'current_zoning': zoning_data.get('code'),
                'description': zoning_data.get('description'),
                'allowed_uses': zoning_data.get('allowed_uses', []),
                'restrictions': {
                    'height': zoning_data.get('height_limit'),
                    'density': zoning_data.get('density_limit'),
                    'setbacks': zoning_data.get('setbacks', {}),
                    'coverage': zoning_data.get('lot_coverage')
                },
                'overlay_districts': zoning_data.get('overlay_districts', []),
                'future_land_use': zoning_data.get('future_land_use'),
                'last_updated': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error extracting zoning data: {str(e)}")
            raise

    def extract_demographics(self, response: Dict) -> Dict:
        """Extract demographic data for the area"""
        try:
            demo_data = response.get('demographics', {})
            return {
                'zipcode': response.get('zipcode', ''),
                'population': {
                    'total': demo_data.get('total_population'),
                    'growth_rate': demo_data.get('population_growth'),
                    'density': demo_data.get('population_density'),
                    'median_age': demo_data.get('median_age')
                },
                'households': {
                    'total': demo_data.get('total_households'),
                    'average_size': demo_data.get('avg_household_size'),
                    'owner_occupied': demo_data.get('owner_occupied_rate'),
                    'renter_occupied': demo_data.get('renter_occupied_rate')
                },
                'income': {
                    'median_household': demo_data.get('median_household_income'),
                    'per_capita': demo_data.get('per_capita_income'),
                    'income_distribution': demo_data.get('income_distribution', {})
                },
                'education': {
                    'high_school': demo_data.get('high_school_rate'),
                    'bachelor': demo_data.get('bachelor_rate'),
                    'graduate': demo_data.get('graduate_rate')
                },
                'employment': {
                    'labor_force': demo_data.get('labor_force_rate'),
                    'unemployment': demo_data.get('unemployment_rate'),
                    'job_growth': demo_data.get('job_growth_rate')
                },
                'last_updated': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error extracting demographic data: {str(e)}")
            raise

    def extract_schools(self, response: Dict) -> Dict:
        """Extract school data for the area"""
        try:
            school_data = response.get('schools', {})
            return {
                'address': self._extract_address(response),
                'assigned_schools': {
                    'elementary': self._extract_school_details(school_data.get('elementary', {})),
                    'middle': self._extract_school_details(school_data.get('middle', {})),
                    'high': self._extract_school_details(school_data.get('high', {}))
                },
                'nearby_schools': [
                    self._extract_school_details(school)
                    for school in school_data.get('nearby', [])
                ],
                'district_info': {
                    'name': school_data.get('district_name'),
                    'rating': school_data.get('district_rating'),
                    'total_schools': school_data.get('total_schools'),
                    'student_teacher_ratio': school_data.get('student_teacher_ratio')
                },
                'last_updated': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error extracting school data: {str(e)}")
            raise

    def extract_risk_assessment(self, response: Dict) -> Dict:
        """Extract property risk assessment data"""
        try:
            risk_data = response.get('risk', {})
            return {
                'address': self._extract_address(response),
                'natural_hazards': {
                    'flood': self._extract_flood_risk(risk_data),
                    'earthquake': self._extract_earthquake_risk(risk_data),
                    'wildfire': self._extract_wildfire_risk(risk_data),
                    'tornado': self._extract_tornado_risk(risk_data),
                    'hurricane': self._extract_hurricane_risk(risk_data)
                },
                'environmental': {
                    'air_quality': risk_data.get('air_quality'),
                    'water_quality': risk_data.get('water_quality'),
                    'soil_contamination': risk_data.get('soil_contamination'),
                    'toxic_sites': risk_data.get('toxic_sites', [])
                },
                'crime': {
                    'overall_rate': risk_data.get('crime_rate'),
                    'violent_crime': risk_data.get('violent_crime_rate'),
                    'property_crime': risk_data.get('property_crime_rate'),
                    'trend': risk_data.get('crime_trend')
                },
                'insurance_factors': {
                    'risk_score': risk_data.get('insurance_risk_score'),
                    'recommended_coverage': risk_data.get('recommended_coverage'),
                    'estimated_premium': risk_data.get('estimated_premium')
                },
                'last_updated': datetime.now()
            }
        except Exception as e:
            self.logger.error(f"Error extracting risk assessment data: {str(e)}")
            raise
    
    # Helper methods for extracting specific data components
    def _extract_address(self, data: Dict) -> Dict:
        """Extract formatted address"""
        address = data.get('address', {})
        return {
            'street': address.get('street'),
            'city': address.get('city'),
            'state': address.get('state'),
            'zipcode': address.get('zip'),
            'formatted': address.get('formatted')
        }
    
    def _extract_basic_info(self, data: Dict) -> Dict:
        """Extract basic property information"""
        return {
            'beds': data.get('beds'),
            'baths': data.get('baths'),
            'sqft': data.get('building_sqft'),
            'year_built': data.get('year_built'),
            'property_type': data.get('property_type'),
            'stories': data.get('stories'),
            'units': data.get('units')
        }
    
    def _extract_construction(self, data: Dict) -> Dict:
        """Extract construction details"""
        return {
            'foundation': data.get('foundation'),
            'roof_type': data.get('roof_type'),
            'exterior_wall': data.get('exterior_wall'),
            'construction_type': data.get('construction_type'),
            'quality': data.get('quality'),
            'condition': data.get('condition')
        }
    
    def _extract_systems(self, data: Dict) -> Dict:
        """Extract property systems information"""
        return {
            'heating': data.get('heating'),
            'cooling': data.get('cooling'),
            'plumbing': data.get('plumbing'),
            'electrical': data.get('electrical'),
            'utilities': data.get('utilities')
        }
    
    def _extract_features(self, data: Dict) -> Dict:
        """Extract property features"""
        return {
            'interior_features': data.get('interior_features', []),
            'exterior_features': data.get('exterior_features', []),
            'amenities': data.get('amenities', []),
            'parking': data.get('parking', {}),
            'pool': data.get('pool')
        }
    
    def _extract_lot_info(self, data: Dict) -> Dict:
        """Extract lot information"""
        return {
            'lot_size': data.get('lot_sqft'),
            'lot_dimensions': data.get('lot_dimensions'),
            'zoning': data.get('zoning'),
            'topography': data.get('topography')
        }
    
    def _extract_tax_value(self, data: Dict) -> Dict:
        """Extract tax value information"""
        return {
            'assessed_value': data.get('assessed_value'),
            'market_value': data.get('market_value'),
            'tax_amount': data.get('tax_amount'),
            'tax_year': data.get('tax_year')
        }
    
    def _extract_tax_history(self, data: Dict) -> List[Dict]:
        """Extract tax assessment history"""
        history = data.get('history', [])
        return [
            {
                'year': item.get('year'),
                'assessed_value': item.get('assessed_value'),
                'market_value': item.get('market_value'),
                'tax_amount': item.get('tax_amount')
            }
            for item in history
        ]
    
    def _extract_exemptions(self, data: Dict) -> List[Dict]:
        """Extract tax exemptions"""
        exemptions = data.get('exemptions', [])
        return [
            {
                'type': item.get('type'),
                'amount': item.get('amount'),
                'year': item.get('year')
            }
            for item in exemptions
        ]
    
    def _extract_historical_values(self, data: Dict) -> List[Dict]:
        """Extract historical property values"""
        history = data.get('history', [])
        return [
            {
                'date': item.get('date'),
                'value': item.get('value'),
                'source': item.get('source')
            }
            for item in history
        ]
    
    def _extract_comps(self, data: Dict) -> List[Dict]:
        """Extract comparable properties"""
        comps = data.get('comps', [])
        return [
            {
                'address': self._extract_address(comp),
                'sale_price': comp.get('sale_price'),
                'sale_date': comp.get('sale_date'),
                'similarity_score': comp.get('similarity_score'),
                'basic_info': self._extract_basic_info(comp)
            }
            for comp in comps
        ]
    
    def _extract_current_owner(self, data: Dict) -> Dict:
        """Extract current owner information"""
        return {
            'name': data.get('name'),
            'type': data.get('owner_type'),
            'occupancy_status': data.get('occupancy_status'),
            'acquisition_date': data.get('acquisition_date')
        }
    
    def _extract_ownership_history(self, data: Dict) -> List[Dict]:
        """Extract ownership history"""
        history = data.get('history', [])
        return [
            {
                'owner_name': item.get('name'),
                'acquisition_date': item.get('acquisition_date'),
                'sale_price': item.get('sale_price'),
                'deed_type': item.get('deed_type')
            }
            for item in history
        ]
    
    def _extract_portfolio(self, data: Dict) -> Dict:
        """Extract owner's property portfolio"""
        portfolio = data.get('portfolio', {})
        return {
            'total_properties': portfolio.get('total_properties'),
            'total_value': portfolio.get('total_value'),
            'property_types': portfolio.get('property_types', {}),
            'geographic_distribution': portfolio.get('geographic_distribution', {})
        }
    
    def _extract_contact_info(self, data: Dict) -> Dict:
        """Extract owner contact information"""
        contact = data.get('contact', {})
        return {
            'mailing_address': contact.get('mailing_address'),
            'phone': contact.get('phone'),
            'email': contact.get('email')
        }
    
    def _extract_price_trends(self, data: Dict) -> Dict:
        """Extract price trend data"""
        trends = data.get('price_trends', {})
        return {
            'median_price': trends.get('median_price'),
            'price_change': trends.get('price_change'),
            'forecast': trends.get('forecast'),
            'historical_trends': trends.get('historical_trends', [])
        }
    
    def _extract_sales_metrics(self, data: Dict) -> Dict:
        """Extract sales metrics"""
        sales = data.get('sales', {})
        return {
            'monthly_sales': sales.get('monthly_sales'),
            'days_on_market': sales.get('days_on_market'),
            'price_per_sqft': sales.get('price_per_sqft'),
            'sale_to_list_ratio': sales.get('sale_to_list_ratio')
        }
    
    def _extract_inventory(self, data: Dict) -> Dict:
        """Extract inventory metrics"""
        inventory = data.get('inventory', {})
        return {
            'active_listings': inventory.get('active_listings'),
            'months_supply': inventory.get('months_supply'),
            'new_listings': inventory.get('new_listings'),
            'price_cuts': inventory.get('price_cuts')
        }
    
    def _extract_rental_metrics(self, data: Dict) -> Dict:
        """Extract rental market metrics"""
        rental = data.get('rental', {})
        return {
            'median_rent': rental.get('median_rent'),
            'rent_change': rental.get('rent_change'),
            'occupancy_rate': rental.get('occupancy_rate'),
            'renter_demographics': rental.get('renter_demographics', {})
        }
    
    def _extract_auction_info(self, data: Dict) -> Dict:
        """Extract foreclosure auction information"""
        auction = data.get('auction', {})
        return {
            'date': auction.get('date'),
            'location': auction.get('location'),
            'opening_bid': auction.get('opening_bid'),
            'auction_status': auction.get('status')
        }
    
    def _extract_default_info(self, data: Dict) -> Dict:
        """Extract default information"""
        default = data.get('default', {})
        return {
            'default_date': default.get('date'),
            'amount': default.get('amount'),
            'type': default.get('type'),
            'status': default.get('status')
        }
    
    def _extract_foreclosure_timeline(self, data: Dict) -> List[Dict]:
        """Extract foreclosure timeline"""
        timeline = data.get('timeline', [])
        return [
            {
                'date': event.get('date'),
                'event_type': event.get('type'),
                'description': event.get('description'),
                'status': event.get('status')
            }
            for event in timeline
        ]

    def _extract_school_details(self, data: Dict) -> Dict:
        """Extract detailed school information"""
        return {
            'name': data.get('name'),
            'type': data.get('type'),
            'grades': data.get('grades'),
            'rating': data.get('rating'),
            'students': data.get('total_students'),
            'teachers': data.get('total_teachers'),
            'ratio': data.get('student_teacher_ratio'),
            'test_scores': {
                'math': data.get('math_score'),
                'reading': data.get('reading_score'),
                'science': data.get('science_score')
            },
            'location': {
                'address': data.get('address'),
                'distance': data.get('distance')
            }
        }

    def _extract_flood_risk(self, data: Dict) -> Dict:
        """Extract flood risk information"""
        flood = data.get('flood', {})
        return {
            'risk_level': flood.get('risk_level'),
            'fema_zone': flood.get('fema_zone'),
            'insurance_required': flood.get('insurance_required'),
            'historical_events': flood.get('historical_events', [])
        }

    def _extract_earthquake_risk(self, data: Dict) -> Dict:
        """Extract earthquake risk information"""
        quake = data.get('earthquake', {})
        return {
            'risk_level': quake.get('risk_level'),
            'seismic_zone': quake.get('seismic_zone'),
            'historical_events': quake.get('historical_events', []),
            'fault_lines': quake.get('nearby_fault_lines', [])
        }

    def _extract_wildfire_risk(self, data: Dict) -> Dict:
        """Extract wildfire risk information"""
        fire = data.get('wildfire', {})
        return {
            'risk_level': fire.get('risk_level'),
            'vegetation_density': fire.get('vegetation_density'),
            'historical_events': fire.get('historical_events', []),
            'defense_space': fire.get('defensible_space')
        }

    def _extract_tornado_risk(self, data: Dict) -> Dict:
        """Extract tornado risk information"""
        tornado = data.get('tornado', {})
        return {
            'risk_level': tornado.get('risk_level'),
            'average_annual': tornado.get('average_annual'),
            'historical_events': tornado.get('historical_events', []),
            'safe_room_recommended': tornado.get('safe_room_recommended')
        }

    def _extract_hurricane_risk(self, data: Dict) -> Dict:
        """Extract hurricane risk information"""
        hurricane = data.get('hurricane', {})
        return {
            'risk_level': hurricane.get('risk_level'),
            'storm_surge_zone': hurricane.get('storm_surge_zone'),
            'historical_events': hurricane.get('historical_events', []),
            'evacuation_zone': hurricane.get('evacuation_zone')
        }
