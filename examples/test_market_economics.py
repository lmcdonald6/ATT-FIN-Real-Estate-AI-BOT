"""Test the Market Economics Analyzer"""

import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from modules.market_economics import analyzer

def test_market_economics():
    # Test different income scenarios for various cities
    test_cases = [
        ("Atlanta", 80000),
        ("Chicago", 100000),
        ("Los Angeles", 150000),
        ("NonExistentCity", 80000)  # Test error handling
    ]
    
    print("\nMarket Economics Analysis")
    print("=" * 60)
    
    for city, income in test_cases:
        print(f"\nAnalyzing: {city}")
        print(f"Household Income: ${income:,}")
        print("-" * 40)
        
        result = analyzer.get_market_score(city, income)
        
        if result.econ_score is not None:
            print(f"Economic Score: {result.econ_score}/100")
            print(f"Market Health: {result.market_health}")
            print(f"Affordability Ratio: {result.affordability_ratio:.2f}")
            print(f"Monthly Sales: {result.monthly_sales:,}")
            print(f"Current Inventory: {result.inventory_level:,}")
            if result.price_to_income:
                print(f"Price-to-Income Ratio: {result.price_to_income:.2f}")
            print(f"\nAnalysis: {result.note}")
            
            if result.warnings:
                print("\nWarnings:")
                for warning in result.warnings:
                    print(f"- {warning}")
        else:
            print(f"Note: {result.note}")
        
        print("-" * 60)

if __name__ == "__main__":
    test_market_economics()
