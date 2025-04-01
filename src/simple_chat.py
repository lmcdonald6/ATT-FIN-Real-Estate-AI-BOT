"""
Real Estate Chat Interface with enhanced query patterns and response formatting
"""
import asyncio
import logging
import os
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RealEstateChatInterface:
    """Interactive chat interface for real estate queries"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.market_data = {}  # Initialize market_data
        
        # Enhanced query patterns
        self.query_patterns = {
            'property_value': [
                'what is the value',
                'how much is',
                'value of',
                'worth',
                'estimate for',
                'valuation of',
                'price of'
            ],
            'property_details': [
                'show me property details',
                'tell me about the property',
                'property info',
                'details for',
                'what condition is',
                'describe the property',
                'features of'
            ],
            'owner_info': [
                'who owns',
                'owner information',
                'tell me about the owner',
                'owner details',
                'who is the owner',
                'owner history',
                'owner background'
            ],
            'occupancy': [
                'is it occupied',
                'occupancy status',
                'vacancy status',
                'is anyone living',
                'is it vacant',
                'tenant status',
                'rental status'
            ],
            'distressed': [
                'show me distressed',
                'find vacant',
                'pre-foreclosures',
                'tax liens',
                'motivated sellers',
                'find distressed',
                'show foreclosures',
                'properties with liens',
                'high equity distressed'
            ],
            'market_analysis': [
                'how is the market',
                'price trends',
                'sales velocity',
                'market conditions',
                'market stats',
                'market overview',
                'market report'
            ],
            'investment': [
                'calculate arv',
                'repairs needed',
                'maximum offer',
                'roi analysis',
                'repair estimate',
                'rehab cost',
                'renovation budget',
                'max purchase price',
                'deal analysis'
            ]
        }
    
    async def process_natural_query(self, user_input: str) -> Dict:
        """Process natural language query"""
        try:
            query_type = self._detect_query_type(user_input.lower())
            
            # Update market data
            self.market_data = {
                'median_price': 175000,
                'avg_days_on_market': 45,
                'active_listings': 120,
                'market_health': 'Strong',
                'demand_level': 'High',
                'price_trends': {
                    '1_month': '+2.3%',
                    '3_month': '+5.8%',
                    '12_month': '+12.4%'
                },
                'sales_metrics': {
                    'velocity': '15 sales/month',
                    'absorption_rate': '2.8 months',
                    'price_reductions': '15%',
                    'sale_to_list_ratio': '97%'
                },
                'rental_metrics': {
                    'average_rent': '$1,200',
                    'vacancy_rate': '3.5%',
                    'rent_growth': '+5.2%'
                },
                'development': {
                    'zoning_changes': 'None pending',
                    'new_construction': 'Limited',
                    'infrastructure': 'Major road improvements planned'
                }
            }
            
            # Enhanced mock response with repair details
            response = {
                'status': 'success',
                'query_type': query_type,
                'properties': [
                    {
                        'address': '123 Main St, Bessemer, AL 35020',
                        'price': 150000,
                        'score': 85,
                        'distress_indicators': ['tax_delinquent', 'vacant'],
                        'property_details': {
                            'beds': 3,
                            'baths': 2,
                            'sqft': 1800,
                            'lot_size': '0.25 acres',
                            'year_built': 1985,
                            'condition': 'Fair',
                            'construction': {
                                'foundation': 'Concrete Slab',
                                'roof': 'Asphalt Shingle',
                                'exterior': 'Brick',
                                'hvac': 'Central',
                                'utilities': ['Electric', 'Gas', 'City Water']
                            },
                            'repairs_needed': {
                                'major': [
                                    'Roof replacement',
                                    'HVAC system upgrade'
                                ],
                                'moderate': [
                                    'Kitchen renovation',
                                    'Bathroom updates'
                                ],
                                'minor': [
                                    'Interior paint',
                                    'Carpet replacement',
                                    'Landscaping'
                                ]
                            }
                        },
                        'financial_metrics': {
                            'arv': 225000,
                            'repair_estimate': 45000,
                            'max_offer': 135000,
                            'potential_roi': 28,
                            'rental_estimate': 1500,
                            'cap_rate': 8.2,
                            'repair_costs': {
                                'major': 25000,
                                'moderate': 15000,
                                'minor': 5000
                            }
                        },
                        'owner_info': {
                            'type': 'absentee',
                            'owned_since': '2010',
                            'tax_status': 'delinquent',
                            'motivation_score': 85,
                            'portfolio_size': 3,
                            'estimated_equity': '45%',
                            'contact_info': {
                                'mailing_address': '789 Different St, Birmingham, AL',
                                'response_rate': '60%',
                                'best_contact_time': 'Evening'
                            }
                        },
                        'distress_factors': {
                            'financial_distress': 85,
                            'time_pressure': 70,
                            'property_condition': 60,
                            'market_position': 75
                        },
                        'lead_status': {
                            'category': 'Hot',
                            'priority': 1,
                            'next_action': 'Direct Mail + Phone Call',
                            'follow_up_date': '2025-03-21'
                        }
                    }
                ],
                'market_data': self.market_data
            }
            
            return response
                
        except Exception as e:
            self.logger.error(f"Error processing natural query: {str(e)}")
            return {
                'status': 'error',
                'message': str(e)
            }
    
    def _detect_query_type(self, user_input: str) -> str:
        """Detect type of query from natural language input"""
        for query_type, patterns in self.query_patterns.items():
            if any(pattern in user_input for pattern in patterns):
                return query_type
        return 'property_search'  # Default type
    
    def format_response(self, response: Dict) -> str:
        """Format response based on query type"""
        if response['status'] == 'error':
            return f"Error: {response['message']}"
        
        query_type = response.get('query_type', 'property_search')
        properties = response.get('properties', [])
        market_data = response.get('market_data', {})
        
        if not properties:
            return "No matching properties found."
            
        output = []
        
        # Header based on query type
        if query_type == 'property_value':
            output.extend(self._format_value_analysis(properties[0]))
        elif query_type == 'property_details':
            output.extend(self._format_property_details(properties[0]))
        elif query_type == 'owner_info':
            output.extend(self._format_owner_info(properties[0]))
        elif query_type == 'occupancy':
            output.extend(self._format_occupancy_status(properties[0]))
        elif query_type == 'distressed':
            output.extend(self._format_distressed_analysis(properties))
        elif query_type == 'market_analysis':
            output.extend(self._format_market_analysis(market_data))
        elif query_type == 'investment':
            output.extend(self._format_investment_analysis(properties[0]))
        else:
            # Default comprehensive view
            output.extend(self._format_comprehensive_view(properties[0]))
        
        return "\n".join(output)
    
    def _format_value_analysis(self, property_data: Dict) -> List[str]:
        """Format property value analysis with enhanced market comparison"""
        metrics = property_data.get('financial_metrics', {})
        details = property_data.get('property_details', {})
        market = self.market_data
        
        price_per_sqft = property_data['price'] / details.get('sqft', 1)
        market_price_per_sqft = market.get('median_price', 0) / details.get('sqft', 1)
        
        return [
            f"Value Analysis: {property_data['address']}",
            "=" * 50,
            "",
            "Current Valuation:",
            f"• Market Value: ${property_data['price']:,}",
            f"• ARV: ${metrics.get('arv', 0):,}",
            f"• Price/Sqft: ${price_per_sqft:,.2f}",
            "",
            "Market Comparison:",
            f"• Neighborhood Median: ${market.get('median_price', 0):,}",
            f"• Market Price/Sqft: ${market_price_per_sqft:,.2f}",
            f"• Price Position: {self._calculate_price_position(property_data['price'])}",
            f"• Days on Market: {market.get('avg_days_on_market', 'N/A')}",
            "",
            "Investment Potential:",
            f"• Estimated Equity: {property_data.get('owner_info', {}).get('estimated_equity', 'N/A')}",
            f"• Repair Estimate: ${metrics.get('repair_estimate', 0):,}",
            f"• Confidence Score: {property_data.get('score', 0)}/100"
        ]
    
    def _format_property_details(self, property_data: Dict) -> List[str]:
        """Format detailed property information with repair needs"""
        details = property_data.get('property_details', {})
        construction = details.get('construction', {})
        repairs = details.get('repairs_needed', {})
        repair_costs = property_data.get('financial_metrics', {}).get('repair_costs', {})
        
        output = [
            f"Property Details: {property_data['address']}",
            "=" * 50,
            "",
            "Basic Information:",
            f"• {details.get('beds', 0)} beds, {details.get('baths', 0)} baths",
            f"• {details.get('sqft', 0):,} sqft",
            f"• Lot Size: {details.get('lot_size', 'N/A')}",
            f"• Year Built: {details.get('year_built', 'N/A')}",
            "",
            "Construction Details:",
            f"• Foundation: {construction.get('foundation', 'N/A')}",
            f"• Roof: {construction.get('roof', 'N/A')}",
            f"• Exterior: {construction.get('exterior', 'N/A')}",
            "",
            "Systems:",
            f"• HVAC: {construction.get('hvac', 'N/A')}",
            f"• Utilities: {', '.join(construction.get('utilities', []))}"
        ]
        
        if repairs:
            output.extend([
                "",
                "Repairs Needed:",
                "Major Repairs: (Est. $" + f"{repair_costs.get('major', 0):,})",
                "• " + "\n• ".join(repairs.get('major', [])),
                "",
                "Moderate Repairs: (Est. $" + f"{repair_costs.get('moderate', 0):,})",
                "• " + "\n• ".join(repairs.get('moderate', [])),
                "",
                "Minor Repairs: (Est. $" + f"{repair_costs.get('minor', 0):,})",
                "• " + "\n• ".join(repairs.get('minor', []))])
        
        return output
    
    def _format_owner_info(self, property_data: Dict) -> List[str]:
        """Format owner information"""
        owner = property_data.get('owner_info', {})
        contact = owner.get('contact_info', {})
        
        return [
            f"Owner Analysis: {property_data['address']}",
            "=" * 50,
            "",
            "Owner Profile:",
            f"• Type: {owner.get('type', 'N/A').replace('_', ' ').title()}",
            f"• Time Owned: {owner.get('owned_since', 'N/A')}",
            f"• Portfolio Size: {owner.get('portfolio_size', 'N/A')} properties",
            "",
            "Financial Status:",
            f"• Tax Status: {owner.get('tax_status', 'N/A').replace('_', ' ').title()}",
            f"• Estimated Equity: {owner.get('estimated_equity', 'N/A')}",
            "",
            "Contact Information:",
            f"• Mailing Address: {contact.get('mailing_address', 'N/A')}",
            f"• Response Rate: {contact.get('response_rate', 'N/A')}",
            f"• Best Contact Time: {contact.get('best_contact_time', 'N/A')}"
        ]
    
    def _format_occupancy_status(self, property_data: Dict) -> List[str]:
        """Format occupancy status with enhanced risk analysis"""
        owner = property_data.get('owner_info', {})
        distress = property_data.get('distress_factors', {})
        details = property_data.get('property_details', {})
        
        return [
            f"Occupancy Analysis: {property_data['address']}",
            "=" * 50,
            "",
            "Current Status:",
            "• " + ("Vacant" if "vacant" in property_data.get('distress_indicators', []) else "Occupied"),
            f"• Owner Type: {owner.get('type', 'N/A').replace('_', ' ').title()}",
            f"• Time at Property: {owner.get('owned_since', 'N/A')}",
            "",
            "Property Condition:",
            f"• Overall Condition: {details.get('condition', 'N/A')}",
            f"• Property Score: {distress.get('property_condition', 0)}/100",
            f"• Major Issues: {len(details.get('repairs_needed', {}).get('major', []))}",
            "",
            "Risk Assessment:",
            f"• Financial Risk: {distress.get('financial_distress', 0)}/100",
            f"• Time Pressure: {distress.get('time_pressure', 0)}/100",
            f"• Market Position: {distress.get('market_position', 0)}/100",
            "",
            "Contact Strategy:",
            f"• Lead Priority: {property_data.get('lead_status', {}).get('priority', 'N/A')}",
            f"• Best Contact Time: {owner.get('contact_info', {}).get('best_contact_time', 'N/A')}",
            f"• Response Rate: {owner.get('contact_info', {}).get('response_rate', 'N/A')}",
            "",
            "Next Steps:",
            f"• Recommended Action: {property_data.get('lead_status', {}).get('next_action', 'N/A')}",
            f"• Follow-up Date: {property_data.get('lead_status', {}).get('follow_up_date', 'N/A')}"
        ]

    def _format_distressed_analysis(self, properties: List[Dict]) -> List[str]:
        """Format distressed property analysis with enhanced lead scoring"""
        output = [
            "Distressed Property Analysis",
            "=" * 50,
            "",
            f"Found {len(properties)} matching properties:",
            ""
        ]
        
        for prop in properties:
            distress = prop.get('distress_factors', {})
            lead = prop.get('lead_status', {})
            owner = prop.get('owner_info', {})
            metrics = prop.get('financial_metrics', {})
            
            output.extend([
                f"Property: {prop['address']}",
                "-" * 40,
                "",
                "Lead Score Analysis:",
                f"• Overall Score: {prop.get('score', 0)}/100",
                f"• Lead Category: {lead.get('category', 'N/A')}",
                f"• Priority Level: {lead.get('priority', 'N/A')}",
                "",
                "Distress Factors:",
                f"• Financial Distress: {distress.get('financial_distress', 0)}/100",
                f"• Time Pressure: {distress.get('time_pressure', 0)}/100",
                f"• Property Condition: {distress.get('property_condition', 0)}/100",
                f"• Market Position: {distress.get('market_position', 0)}/100",
                "",
                "Owner Status:",
                f"• Type: {owner.get('type', 'N/A').replace('_', ' ').title()}",
                f"• Tax Status: {owner.get('tax_status', 'N/A').replace('_', ' ').title()}",
                f"• Estimated Equity: {owner.get('estimated_equity', 'N/A')}",
                f"• Response Rate: {owner.get('contact_info', {}).get('response_rate', 'N/A')}",
                "",
                "Property Metrics:",
                f"• Current Value: ${prop.get('price', 0):,}",
                f"• Repair Estimate: ${metrics.get('repair_estimate', 0):,}",
                f"• Max Offer: ${metrics.get('max_offer', 0):,}",
                f"• Potential ROI: {metrics.get('potential_roi', 0)}%",
                "",
                "Action Plan:",
                f"• Next Action: {lead.get('next_action', 'N/A')}",
                f"• Follow-up Date: {lead.get('follow_up_date', 'N/A')}",
                f"• Best Contact Time: {owner.get('contact_info', {}).get('best_contact_time', 'N/A')}",
                "",
                "=" * 50,
                ""
            ])
        
        return output
    
    def _format_market_analysis(self, market_data: Dict) -> List[str]:
        """Format comprehensive market analysis"""
        trends = market_data.get('price_trends', {})
        sales = market_data.get('sales_metrics', {})
        rental = market_data.get('rental_metrics', {})
        dev = market_data.get('development', {})
        
        return [
            "Market Analysis Report",
            "=" * 50,
            "",
            "Price Trends & Velocity:",
            f"• 1 Month Change: {trends.get('1_month', 'N/A')}",
            f"• 3 Month Change: {trends.get('3_month', 'N/A')}",
            f"• 12 Month Change: {trends.get('12_month', 'N/A')}",
            f"• Sales Velocity: {sales.get('velocity', 'N/A')}",
            "",
            "Market Conditions:",
            f"• Days on Market: {market_data.get('avg_days_on_market', 'N/A')}",
            f"• Active Listings: {market_data.get('active_listings', 'N/A')}",
            f"• Absorption Rate: {sales.get('absorption_rate', 'N/A')}",
            f"• Sale/List Ratio: {sales.get('sale_to_list_ratio', 'N/A')}",
            "",
            "Rental Market:",
            f"• Average Rent: {rental.get('average_rent', 'N/A')}",
            f"• Vacancy Rate: {rental.get('vacancy_rate', 'N/A')}",
            f"• Rent Growth: {rental.get('rent_growth', 'N/A')}",
            f"• Price Reductions: {sales.get('price_reductions', 'N/A')}",
            "",
            "Market Health Indicators:",
            f"• Overall Health: {market_data.get('market_health', 'N/A')}",
            f"• Demand Level: {market_data.get('demand_level', 'N/A')}",
            f"• Inventory Level: Low",
            "",
            "Development Activity:",
            f"• Zoning Changes: {dev.get('zoning_changes', 'N/A')}",
            f"• New Construction: {dev.get('new_construction', 'N/A')}",
            f"• Infrastructure: {dev.get('infrastructure', 'N/A')}"
        ]

    def _format_investment_analysis(self, property_data: Dict) -> List[str]:
        """Format comprehensive investment analysis"""
        metrics = property_data.get('financial_metrics', {})
        details = property_data.get('property_details', {})
        repairs = details.get('repairs_needed', {})
        repair_costs = metrics.get('repair_costs', {})
        
        return [
            f"Investment Analysis: {property_data['address']}",
            "=" * 50,
            "",
            "Purchase Analysis:",
            f"• Current Price: ${property_data['price']:,}",
            f"• Max Offer: ${metrics.get('max_offer', 0):,}",
            f"• Price/Sqft: ${property_data['price'] / details.get('sqft', 1):,.2f}",
            "",
            "Renovation Budget:",
            f"• Total Repairs: ${metrics.get('repair_estimate', 0):,}",
            f"• Major Repairs: ${repair_costs.get('major', 0):,}",
            f"• Moderate Repairs: ${repair_costs.get('moderate', 0):,}",
            f"• Minor Repairs: ${repair_costs.get('minor', 0):,}",
            "",
            "After Repair Value:",
            f"• ARV: ${metrics.get('arv', 0):,}",
            f"• Market Position: {self._calculate_price_position(metrics.get('arv', 0))}",
            f"• Confidence Score: {property_data.get('score', 0)}/100",
            "",
            "Rental Potential:",
            f"• Monthly Rent: ${metrics.get('rental_estimate', 0):,}",
            f"• Cap Rate: {metrics.get('cap_rate', 0)}%",
            f"• Market Rent Growth: {self.market_data.get('rental_metrics', {}).get('rent_growth', 'N/A')}",
            "",
            "Returns:",
            f"• Potential ROI: {metrics.get('potential_roi', 0)}%",
            f"• Estimated Equity: {property_data.get('owner_info', {}).get('estimated_equity', 'N/A')}",
            f"• Time to ROI: {self.market_data.get('sales_metrics', {}).get('absorption_rate', 'N/A')}"
        ]
    
    def _format_comprehensive_view(self, property_data: Dict) -> List[str]:
        """Format comprehensive property view"""
        output = []
        
        # Combine all analysis sections
        output.extend(self._format_property_details(property_data))
        output.extend(["", "=" * 50, ""])
        output.extend(self._format_value_analysis(property_data))
        output.extend(["", "=" * 50, ""])
        output.extend(self._format_owner_info(property_data))
        output.extend(["", "=" * 50, ""])
        output.extend(self._format_investment_analysis(property_data))
        
        return output
    
    def _calculate_price_position(self, price: float) -> str:
        """Calculate price position relative to market"""
        median = self.market_data.get('median_price', price)
        diff = ((price - median) / median) * 100
        
        if diff <= -20:
            return "Significantly Below Market"
        elif diff <= -10:
            return "Below Market"
        elif diff <= 10:
            return "At Market"
        elif diff <= 20:
            return "Above Market"
        else:
            return "Significantly Above Market"

async def main():
    """Main chat loop"""
    try:
        chat = RealEstateChatInterface()
        print("\nWelcome to the Real Estate AI Bot!")
        print("Ask me about properties in Bessemer, AL")
        print("Type 'quit' to exit\n")
        
        while True:
            try:
                user_input = input("> ")
                if user_input.lower() in ['quit', 'exit']:
                    print("\nGoodbye!")
                    break
                
                response = await chat.process_natural_query(user_input)
                print("\n" + chat.format_response(response) + "\n")
                
            except EOFError:
                print("\nGoodbye!")
                break
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"\nError: {str(e)}\n")
                
    except Exception as e:
        print(f"Failed to initialize chat interface: {str(e)}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nGoodbye!")
    except EOFError:
        print("\nGoodbye!")
