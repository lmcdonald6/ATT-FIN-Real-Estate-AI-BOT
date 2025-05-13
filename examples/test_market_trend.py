"""Test the Market Trend Analyzer"""

import os
import sys

# Add the src directory to the Python path
sys.path.append(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from modules.market_trend import analyzer

def test_market_trends():
    # Test regions
    test_regions = [
        "Atlanta",
        "Chicago",
        "Los Angeles",
        "NonExistentCity"  # Test error handling
    ]
    
    print("\nMarket Trend Analysis")
    print("=" * 50)
    
    for region in test_regions:
        print(f"\nAnalyzing: {region}")
        print("-" * 30)
        
        result = analyzer.get_trend_score(region)
        
        if result.trend_score is not None:
            print(f"Trend Score: {result.trend_score}/100")
            print(f"Avg. Monthly Appreciation: {result.avg_appreciation*100:.2f}%")
            print(f"Price Volatility: {result.volatility*100:.2f}%")
            print(f"Analysis: {result.note}")
            
            # Show raw data summary if available
            if result.raw_data:
                recent_prices = result.raw_data["price_history"][-3:]
                print("\nRecent Prices:")
                for i, price in enumerate(recent_prices):
                    print(f"  Month {len(recent_prices)-i}: ${price:,.0f}")
        else:
            print(f"Note: {result.note}")
        
        print("-" * 50)

if __name__ == "__main__":
    test_market_trends()
