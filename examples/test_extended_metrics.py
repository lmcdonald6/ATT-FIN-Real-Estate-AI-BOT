"""Test the Extended Market Metrics Analyzer"""

import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from modules.extended_market_metrics import analyzer

def test_extended_metrics():
    # Test cities
    test_cities = [
        "Atlanta",
        "Chicago",
        "Los Angeles",
        "NonExistentCity"  # Test error handling
    ]
    
    print("\nExtended Market Metrics Analysis")
    print("=" * 70)
    
    for city in test_cities:
        print(f"\nAnalyzing: {city}")
        print("-" * 50)
        
        result = analyzer.get_extended_metrics(city)
        
        if result.investment_score is not None:
            print(f"Investment Score: {result.investment_score}/100")
            print(f"Market Phase: {result.market_phase}")
            print(f"Risk Level: {result.risk_level}")
            
            print("\nKey Metrics:")
            print(f"- Price-to-Rent Ratio: {result.price_to_rent_ratio:.2f}")
            print(f"- Rental Yield: {result.rental_yield_pct:.1f}%")
            print(f"- Cost of Living Index: {result.cost_of_living_index:.1f}")
            print(f"- Active Construction Permits: {result.active_permits}")
            print(f"- Market Saturation Index: {result.saturation_index:.2f}")
            
            if result.opportunities:
                print("\nOpportunities:")
                for opp in result.opportunities:
                    print(f"+ {opp}")
                    
            if result.concerns:
                print("\nConcerns:")
                for concern in result.concerns:
                    print(f"- {concern}")
            
            print(f"\nAnalysis: {result.note}")
        else:
            print(f"Note: {result.note}")
        
        print("-" * 70)

if __name__ == "__main__":
    test_extended_metrics()
