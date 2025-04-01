"""
Test script for enhanced market analysis system.
Tests both mock data generation and ML predictions.
"""
import asyncio
from src.data.manager import DataManager
from src.analysis.market_analyzer import MarketAnalyzer
from src.ml.market_predictor import MarketPredictor

async def test_market_analysis():
    """Test market analysis and predictions."""
    print("Testing Enhanced Market Analysis System")
    print("=" * 50)
    
    # Initialize components
    data_manager = DataManager()
    market_analyzer = MarketAnalyzer()
    market_predictor = MarketPredictor()
    
    # Test markets
    test_markets = {
        "Nashville Luxury": "37215",
        "Atlanta Urban": "30308",
        "Dallas Prime": "75225"
    }
    
    for market_name, zip_code in test_markets.items():
        print(f"\nAnalyzing {market_name} (ZIP: {zip_code})")
        print("-" * 50)
        
        # Get market stats
        stats = market_analyzer.get_market_stats(zip_code)
        print("\nMarket Statistics:")
        print(f"Median Price: ${stats['median_price']:,.2f}")
        print(f"Annual Price Trend: {stats['price_trend']*100:.1f}%")
        print(f"Inventory Trend: {stats['inventory_trend']*100:.1f}%")
        print(f"Median Days on Market: {stats['median_dom']:.1f}")
        
        # Get sample properties
        properties = await data_manager.search_properties(zip_code)
        if not properties:
            print("No properties found")
            continue
        
        # Analyze sample property
        sample_property = properties[0]
        sample_property['zip_code'] = zip_code
        
        # Get market predictions
        predictions = market_predictor.predict_market_trends(
            zip_code,
            stats,
            months_ahead=12
        )
        
        print("\nMarket Predictions (12 months):")
        print(f"Price Change: {predictions['price_change']:.1f}%")
        print(f"Inventory Change: {predictions['inventory_change']:.1f}%")
        print(f"Market Direction: {predictions['market_direction']}")
        print(f"Confidence Score: {predictions['confidence_score']:.2f}")
        
        # Analyze investment potential
        investment = market_predictor.analyze_investment_potential(
            sample_property,
            predictions
        )
        
        print("\nInvestment Analysis (Sample Property):")
        print(f"Investment Score: {investment['investment_score']}/100")
        print(f"Price Score: {investment['price_score']}/100")
        print(f"Location Score: {investment['location_score']}/100")
        print(f"Property Score: {investment['property_score']}/100")
        print(f"Risk Level: {investment['risk_level']}")
        
        print("\nAppreciation Potential:")
        print(f"Conservative: {investment['estimated_appreciation']['conservative']}%")
        print(f"Moderate: {investment['estimated_appreciation']['moderate']}%")
        print(f"Optimistic: {investment['estimated_appreciation']['optimistic']}%")

if __name__ == "__main__":
    asyncio.run(test_market_analysis())
