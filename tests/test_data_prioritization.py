"""Test Data Prioritization System"""
from src.data_prioritizer import DataPrioritizer
from datetime import datetime

def test_property_analysis():
    """Test property analysis with data source prioritization"""
    prioritizer = DataPrioritizer()
    
    # Sample property data from Redfin
    redfin_data = {
        'price': 250000,
        'beds': 3,
        'baths': 2,
        'sqft': 1800,
        'year_built': 1985,
        'days_on_market': 95,
        'price_history': [
            {'date': '2024-12-01', 'price': 275000},
            {'date': '2025-01-15', 'price': 265000},
            {'date': '2025-03-01', 'price': 250000}
        ],
        'condition_score': 65,
        'maintenance_needed': True,
        'market_trend': 'declining',
        'overpriced_vs_comps': True
    }
    
    # Sample property data from ATTOM (only what's missing from Redfin)
    attom_data = {
        'tax_delinquent': True,
        'foreclosure_status': 'Pre-foreclosure',
        'liens': True,
        'avm_value': 230000
    }
    
    # Combine data (in real usage, this would be fetched as needed)
    property_data = {**redfin_data, **attom_data}
    
    print("\nProperty Analysis Example")
    print("=======================")
    
    # 1. Check data source for each field
    print("\n1. Data Source Analysis")
    print("---------------------")
    fields_to_check = [
        'price', 'beds', 'condition_score',  # Redfin fields
        'tax_delinquent', 'foreclosure_status'  # ATTOM fields
    ]
    
    for field in fields_to_check:
        source = prioritizer.get_data_source(field)
        print(f"• {field}: {source.title()}")
    
    # 2. Calculate lead score using prioritized data
    print("\n2. Lead Scoring (Using Both Sources)")
    print("----------------------------------")
    lead_score = prioritizer.calculate_lead_score(property_data)
    
    print(f"Total Score: {lead_score['total_score']}/100")
    print("\nComponent Scores:")
    for component, score in lead_score['components'].items():
        print(f"• {component}: {score}/100")
    
    print(f"\nLead Status: {lead_score['status']}")
    
    print("\nData Sources Used:")
    for source, fields in lead_score['data_sources'].items():
        print(f"• {source}: {', '.join(fields)}")
    
    # 3. Check refresh requirements
    print("\n3. Data Refresh Analysis")
    print("----------------------")
    fields_to_refresh = {
        'foreclosure_status': 'high_frequency',
        'price': 'high_frequency',
        'owner_info': 'low_frequency',
        'tax_info': 'low_frequency'
    }
    
    for field, frequency in fields_to_refresh.items():
        days = prioritizer.refresh_rules[frequency]['days']
        sources = prioritizer.refresh_rules[frequency]['source_priority']
        print(f"\n• {field}:")
        print(f"  - Refresh every {days} days")
        print(f"  - Source priority: {' -> '.join(sources)}")
    
    # 4. Get recommended actions
    print("\n4. Recommended Actions")
    print("-------------------")
    actions = lead_score['recommended_action']
    for action in actions:
        print(f"\nPriority {action['priority']}:")
        print(f"• Action: {action['action']}")
        print(f"• Reason: {action['reason']}")
        print(f"• Method: {action['method']}")
    
    # 5. Cost Analysis
    print("\n5. Cost Analysis")
    print("-------------")
    redfin_fields_used = len([f for f in fields_to_check if prioritizer.get_data_source(f) == 'redfin'])
    attom_fields_used = len([f for f in fields_to_check if prioritizer.get_data_source(f) == 'attom'])
    
    cost_per_attom_call = 0.05
    potential_cost = len(fields_to_check) * cost_per_attom_call
    actual_cost = attom_fields_used * cost_per_attom_call
    savings = potential_cost - actual_cost
    
    print(f"Fields checked: {len(fields_to_check)}")
    print(f"Redfin fields used: {redfin_fields_used} (Free)")
    print(f"ATTOM fields used: {attom_fields_used} (${actual_cost:.2f})")
    print(f"Potential cost without prioritization: ${potential_cost:.2f}")
    print(f"Cost savings: ${savings:.2f}")

if __name__ == "__main__":
    test_property_analysis()
