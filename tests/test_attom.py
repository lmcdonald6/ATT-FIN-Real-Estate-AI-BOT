"""Test ATTOM API Integration"""
from src.real_estate_qa import RealEstateQA

def main():
    qa = RealEstateQA()
    
    # Test property
    address = "123 Main St"
    zipcode = "90210"  # Beverly Hills
    
    print("\nAnalyzing property...")
    property_data = qa.analyze_property(address, zipcode)
    print("\nProperty Analysis:")
    print(f"• Market Value: {property_data['market_value']}")
    print(f"• Details: {property_data['property_details']['beds']}bed/{property_data['property_details']['baths']}bath, {property_data['property_details']['sqft']}sqft")
    print(f"• Rental Estimate: {property_data['rental_estimate']}")
    
    print("\nGetting investment analysis...")
    investment = qa.analyze_investment(address, zipcode)
    print("\nInvestment Analysis:")
    print(f"• ARV: {investment['arv']}")
    print(f"• Repair Estimate: {investment['repair_estimate']}")
    print(f"• Maximum Offer: {investment['max_offer']}")
    print(f"• ROI: {investment['metrics']['roi']}")
    
    print("\nChecking lead score...")
    lead = qa.get_lead_score(address, zipcode)
    print("\nLead Analysis:")
    print(f"• Total Score: {lead['total_score']}/100")
    print(f"• Status: {lead['status']}")
    print(f"• Action: {lead['recommended_action']}")
    if lead['motivation_factors']:
        print("• Motivation Factors:")
        for factor in lead['motivation_factors']:
            print(f"  - {factor}")

if __name__ == "__main__":
    main()
