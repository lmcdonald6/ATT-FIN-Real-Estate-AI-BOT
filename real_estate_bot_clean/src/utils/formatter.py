"""
Response Formatter
Handles structured formatting of property analysis responses.
"""

from typing import Dict, List
import logging
from datetime import datetime

class ResponseFormatter:
    def __init__(self):
        self.logger = logging.getLogger(__name__)

    def format_value_analysis(self, property_data: Dict) -> List[str]:
        """Format value analysis with market comparison."""
        return [
            f"Value Analysis: {property_data['address']}",
            "=" * 50,
            "",
            "Current Valuation:",
            f"• Market Value: ${property_data['price']:,}",
            f"• ARV: ${property_data.get('financial_metrics', {}).get('arv', 0):,}",
            f"• Price/Sqft: ${property_data['price'] / property_data.get('property_details', {}).get('sqft', 1):,.2f}",
            "",
            "Market Comparison:",
            f"• Neighborhood Median: ${property_data.get('market_data', {}).get('median_price', 175000):,}",
            f"• Market Price/Sqft: ${property_data.get('market_data', {}).get('price_per_sqft', 97.22):,.2f}",
            f"• Price Position: {self._calculate_price_position(property_data['price'])}",
            f"• Days on Market: {property_data.get('days_on_market', 45)}",
            "",
            "Investment Potential:",
            f"• Estimated Equity: {property_data.get('owner_info', {}).get('estimated_equity', '45%')}",
            f"• Repair Estimate: ${property_data.get('financial_metrics', {}).get('repair_estimate', 0):,}",
            f"• Confidence Score: {property_data.get('score', 85)}/100"
        ]

    def format_property_details(self, property_data: Dict) -> List[str]:
        """Format comprehensive property details."""
        details = property_data.get('property_details', {})
        repairs = details.get('repairs_needed', {})
        
        output = [
            f"Property Details: {property_data['address']}",
            "=" * 50,
            "",
            "Basic Information:",
            f"• {details.get('beds', 0)} beds, {details.get('baths', 0)} baths",
            f"• {details.get('sqft', 0):,} sqft",
            f"• Lot Size: {details.get('lot_size', 0)} acres",
            f"• Year Built: {details.get('year_built', 0)}",
            "",
            "Construction Details:",
            f"• Foundation: {details.get('foundation', 'Concrete Slab')}",
            f"• Roof: {details.get('roof', 'Asphalt Shingle')}",
            f"• Exterior: {details.get('exterior', 'Brick')}",
            "",
            "Systems:",
            f"• HVAC: {details.get('hvac', 'Central')}",
            f"• Utilities: {', '.join(details.get('utilities', ['Electric', 'Gas', 'City Water']))}"
        ]

        if repairs:
            output.extend([
                "",
                "Repairs Needed:",
                f"Major Repairs: (Est. ${property_data.get('financial_metrics', {}).get('repair_costs', {}).get('major', 25000):,})"
            ])
            output.extend([f"• {repair}" for repair in repairs.get('major', [])])
            
            output.extend([
                "",
                f"Moderate Repairs: (Est. ${property_data.get('financial_metrics', {}).get('repair_costs', {}).get('moderate', 15000):,})"
            ])
            output.extend([f"• {repair}" for repair in repairs.get('moderate', [])])
            
            output.extend([
                "",
                f"Minor Repairs: (Est. ${property_data.get('financial_metrics', {}).get('repair_costs', {}).get('minor', 5000):,})"
            ])
            output.extend([f"• {repair}" for repair in repairs.get('minor', [])])

        return output

    def format_owner_analysis(self, property_data: Dict) -> List[str]:
        """Format owner analysis with contact strategy."""
        owner = property_data.get('owner_info', {})
        
        return [
            f"Owner Analysis: {property_data['address']}",
            "=" * 50,
            "",
            "Owner Profile:",
            f"• Type: {owner.get('type', 'N/A')}",
            f"• Time Owned: {owner.get('time_owned', 'N/A')}",
            f"• Portfolio Size: {owner.get('portfolio_size', 3)} properties",
            "",
            "Financial Status:",
            f"• Tax Status: {owner.get('tax_status', 'N/A')}",
            f"• Estimated Equity: {owner.get('estimated_equity', 'N/A')}",
            "",
            "Contact Information:",
            f"• Mailing Address: {owner.get('mailing_address', '789 Different St, Birmingham, AL')}",
            f"• Response Rate: {owner.get('contact_info', {}).get('response_rate', 'N/A')}",
            f"• Best Contact Time: {owner.get('contact_info', {}).get('best_contact_time', 'N/A')}"
        ]

    def format_occupancy_status(self, property_data: Dict) -> List[str]:
        """Format occupancy status with risk analysis."""
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

    def format_distressed_analysis(self, properties: List[Dict]) -> List[str]:
        """Format distressed property analysis with lead scoring."""
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

    def format_market_analysis(self, market_data: Dict) -> List[str]:
        """Format comprehensive market analysis."""
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

    def format_investment_analysis(self, property_data: Dict) -> List[str]:
        """Format comprehensive investment analysis."""
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

    def _calculate_price_position(self, price: float) -> str:
        """Calculate market position relative to median."""
        median = 175000  # Example median price
        ratio = price / median
        
        if ratio > 1.2:
            return "Significantly Above Market"
        elif ratio > 1.05:
            return "Above Market"
        elif ratio > 0.95:
            return "At Market"
        elif ratio > 0.8:
            return "Below Market"
        else:
            return "Significantly Below Market"
