import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.ai.smart_insights import SmartInsightsEngine
from src.ai.agent import RealEstateAIAgent
import pandas as pd
from datetime import datetime, timedelta
import json

def generate_test_data():
    """Generate test data for insights engine"""
    # Generate historical market data
    dates = pd.date_range(start='2023-01-01', end='2024-01-01', freq='D')
    prices = [350000 + i * 100 + (i % 30) * 1000 for i in range(len(dates))]
    
    historical_data = pd.DataFrame({
        'date': dates,
        'price': prices,
        'days_on_market': [30 + (i % 15) for i in range(len(dates))]
    })
    
    # Generate property data
    property_data = {
        'id': 'TEST001',
        'price': 375000,
        'square_feet': 2000,
        'beds': 3,
        'baths': 2,
        'year_built': 1990,
        'condition': 'good',
        'location': 'Beverly Hills',
        'lot_size': 5000,
        'features': ['garage', 'pool', 'updated kitchen'],
        'zoning': 'R1'
    }
    
    # Generate market data
    market_data = {
        'median_price': 400000,
        'avg_price_per_sqft': 200,
        'avg_rent_per_sqft': 2,
        'annual_growth_rate': 0.05,
        'market_stability': 0.8,
        'location_score': 0.9,
        'historical_data': historical_data.to_dict('records')
    }
    
    return property_data, market_data

def test_insights_engine():
    """Test the SmartInsightsEngine functionality"""
    print("\nTesting SmartInsightsEngine...")
    
    # Initialize engine
    engine = SmartInsightsEngine()
    
    # Get test data
    property_data, market_data = generate_test_data()
    
    # Test opportunity score
    print("\nTesting Opportunity Score...")
    opportunity = engine.calculate_opportunity_score(property_data, market_data)
    print(f"Opportunity Score: {opportunity.score:.2f}")
    print("Factors:", json.dumps(opportunity.factors, indent=2))
    print("Recommendations:", json.dumps(opportunity.recommendations, indent=2))
    
    # Test market patterns
    print("\nTesting Market Pattern Analysis...")
    historical_df = pd.DataFrame(market_data['historical_data'])
    insights = engine.analyze_market_patterns(historical_df)
    for insight in insights:
        print(f"\nTrend: {insight.trend}")
        print(f"Confidence: {insight.confidence:.1f}%")
        print(f"Impact: {insight.impact}")
        print(f"Action Items: {json.dumps(insight.action_items, indent=2)}")
    
    # Test investment strategy
    print("\nTesting Investment Strategy Generation...")
    investor_profile = {
        'risk_tolerance': 'medium',
        'investment_horizon': 'long',
        'goals': ['passive_income', 'appreciation']
    }
    
    strategy = engine.generate_investment_strategy(property_data, market_data, investor_profile)
    print("Investment Strategy:", json.dumps(strategy, indent=2))
    
    # Test market clustering
    print("\nTesting Market Clustering...")
    properties = [
        property_data,
        {**property_data, 'id': 'TEST002', 'price': 425000, 'condition': 'excellent'},
        {**property_data, 'id': 'TEST003', 'price': 325000, 'condition': 'fair'}
    ]
    
    clusters = engine.identify_market_clusters(properties)
    print("Market Clusters:", json.dumps(clusters, indent=2))

def test_ai_agent():
    """Test the RealEstateAIAgent functionality"""
    print("\nTesting RealEstateAIAgent...")
    
    # Initialize agent with OpenAI API key
    agent = RealEstateAIAgent(os.getenv('OPENAI_API_KEY'))
    
    # Get test data
    property_data, market_data = generate_test_data()
    
    # Test property analysis
    print("\nTesting Property Analysis...")
    analysis = agent.analyze_property(property_data, market_data)
    print("Property Analysis:", json.dumps(analysis, indent=2))
    
    # Test message processing
    print("\nTesting Message Processing...")
    test_messages = [
        "I'm looking for investment properties in Beverly Hills under $500k",
        "What's the current market trend in this area?",
        "Can you analyze this property for a potential flip?"
    ]
    
    for message in test_messages:
        print(f"\nProcessing message: {message}")
        response = agent.process_message(message)
        print("Response:", json.dumps(response, indent=2))
    
    # Test preference updates
    print("\nTesting Preference Updates...")
    preferences = {
        'price_range': {'min': 300000, 'max': 500000},
        'location': 'Beverly Hills',
        'property_type': 'single_family',
        'features': ['garage', 'pool']
    }
    
    agent.update_preferences(preferences)
    
    # Test property recommendations
    print("\nTesting Property Recommendations...")
    properties = [
        property_data,
        {**property_data, 'id': 'TEST002', 'price': 425000, 'condition': 'excellent'},
        {**property_data, 'id': 'TEST003', 'price': 325000, 'condition': 'fair'}
    ]
    
    recommendations = agent.get_property_recommendations(properties)
    print("Property Recommendations:", json.dumps(recommendations, indent=2))

if __name__ == "__main__":
    # Run tests
    test_insights_engine()
    test_ai_agent()
