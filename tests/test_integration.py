"""Integration Test for Real Estate AI Bot"""
from src.integrations.attom_api import AttomAPI
from src.data_prioritizer import DataPrioritizer
from src.response_formatter import ResponseFormatter
from datetime import datetime
import json

def test_full_property_analysis():
    """Test complete property analysis workflow"""
    
    # Initialize components
    attom = AttomAPI()
    prioritizer = DataPrioritizer()
    formatter = ResponseFormatter()
    
    # Sample property data
    test_property = {
        'address': '123 Main St',
        'zipcode': '12345',
        
        # Redfin Data (Free)
        'price': 250000,
        'beds': 3,
        'baths': 2,
        'sqft': 1800,
        'year_built': 1985,
        'days_on_market': 95,
        'condition_score': 65,
        'price_history': [
            {'date': '2024-12-01', 'price': 275000},
            {'date': '2025-01-15', 'price': 265000},
            {'date': '2025-03-01', 'price': 250000}
        ],
        
        # ATTOM Data (Paid)
        'avm_value': 230000,
        'tax_delinquent': True,
        'foreclosure_status': 'Pre-foreclosure',
        'liens': [{'amount': 5000, 'type': 'Tax Lien'}],
        'owner_name': 'John Smith',
        'mailing_address': '456 Other St',
        'length_of_residence': 8,
        'occupancy_status': 'Owner Occupied',
        'utility_status': 'Active',
        'assessed_value': 220000,
        
        # Market Data
        'median_price': 260000,
        'inventory_months': 4.5,
        'monthly_sales': 25,
        'price_reduced_ratio': 35,
        'absorption_rate': 15,
        
        # Investment Analysis
        'arv': 300000,
        'repair_cost': 40000,
        'major_repairs': ['Roof', 'HVAC'],
        'arv_comps': [
            {'address': '789 Comp St', 'similarity': 95, 'price': 305000},
            {'address': '321 Similar Ln', 'similarity': 90, 'price': 295000}
        ]
    }
    
    print("\nReal Estate AI Bot - Integration Test")
    print("====================================")
    
    # 1. Test Property Analysis
    print("\n1. Property Analysis & Valuation")
    print("------------------------------")
    property_analysis = formatter.format_property_analysis(test_property)
    print(json.dumps(property_analysis, indent=2))
    
    # 2. Test Seller Insights
    print("\n2. Seller & Ownership Insights")
    print("----------------------------")
    seller_insights = formatter.format_seller_insights(test_property)
    print(json.dumps(seller_insights, indent=2))
    
    # 3. Test Distressed Property Analysis
    print("\n3. Distressed Property Analysis")
    print("-----------------------------")
    distressed_analysis = formatter.format_distressed_property(test_property)
    print(json.dumps(distressed_analysis, indent=2))
    
    # 4. Test Market Analysis
    print("\n4. Market Analysis")
    print("---------------")
    market_analysis = formatter.format_market_analysis(test_property)
    print(json.dumps(market_analysis, indent=2))
    
    # 5. Test Investment Analysis
    print("\n5. Investment Analysis")
    print("-------------------")
    investment_analysis = formatter.format_investment_analysis(test_property)
    print(json.dumps(investment_analysis, indent=2))
    
    # 6. Test Lead Scoring
    print("\n6. Lead Scoring")
    print("-------------")
    lead_score = formatter.format_lead_score({
        'total_score': 85,
        'financial_distress': 90,
        'time_pressure': 70,
        'property_condition': 65,
        'market_position': 80,
        'phone': '555-0123',
        'mailing_address': '456 Other St',
        'occupancy_status': 'Owner Occupied'
    })
    print(json.dumps(lead_score, indent=2))
    
    # 7. Data Source Analysis
    print("\n7. Data Source & Cost Analysis")
    print("--------------------------")
    
    # Count fields by source
    redfin_fields = ['price', 'beds', 'baths', 'sqft', 'year_built', 
                     'days_on_market', 'condition_score', 'price_history']
    attom_fields = ['avm_value', 'tax_delinquent', 'foreclosure_status', 
                    'liens', 'owner_name', 'assessed_value']
    
    redfin_count = len([f for f in test_property.keys() if f in redfin_fields])
    attom_count = len([f for f in test_property.keys() if f in attom_fields])
    
    # Calculate costs
    cost_per_attom_call = 0.05
    potential_cost = len(test_property) * cost_per_attom_call
    actual_cost = attom_count * cost_per_attom_call
    savings = potential_cost - actual_cost
    
    print(f"\nData Sources Used:")
    print(f"• Redfin fields: {redfin_count} (Free)")
    print(f"• ATTOM fields: {attom_count} (${actual_cost:.2f})")
    print(f"• Total fields: {len(test_property)}")
    print(f"\nCost Analysis:")
    print(f"• Potential cost without prioritization: ${potential_cost:.2f}")
    print(f"• Actual cost with prioritization: ${actual_cost:.2f}")
    print(f"• Cost savings: ${savings:.2f}")
    
    # 8. Refresh Rules
    print("\n8. Data Refresh Rules")
    print("------------------")
    refresh_rules = {
        'foreclosure_status': {'frequency': 'daily', 'source': 'ATTOM'},
        'price': {'frequency': 'daily', 'source': 'Redfin'},
        'owner_info': {'frequency': 'monthly', 'source': 'Cache'},
        'property_details': {'frequency': 'weekly', 'source': 'Redfin'}
    }
    
    for field, rule in refresh_rules.items():
        print(f"\n• {field}:")
        print(f"  - Refresh: {rule['frequency']}")
        print(f"  - Source: {rule['source']}")

if __name__ == "__main__":
    test_full_property_analysis()
