"""Configuration settings for the Real Estate AI Bot"""

# API Configuration
ATTOM_API = {
    'base_url': 'https://api.gateway.attomdata.com/propertyapi/v1.0.0',
    'endpoints': {
        'property_details': '/property/detail',
        'property_address': '/property/address',
        'market_stats': '/market/snapshot',
        'foreclosure': '/foreclosure'
    },
    'batch_size': 10,
    'rate_limit': 100  # requests per minute
}

REDFIN_API = {
    'base_url': 'https://www.redfin.com/stingray/api/gis',
    'endpoints': {
        'market_data': '/market-data',
        'property_details': '/property-details',
        'comparables': '/comparables'
    }
}

# Firebase Configuration
FIREBASE_CONFIG = {
    'collections': {
        'properties': 'properties',
        'queries': 'query_cache',
        'metrics': 'search_metrics',
        'feedback': 'user_feedback'
    },
    'cache_duration_days': 30
}

# Scoring Weights
LEAD_SCORE_WEIGHTS = {
    'financial_distress': 0.35,
    'property_condition': 0.25,
    'market_position': 0.20,
    'timing': 0.20
}

# Response Formatting
CURRENCY_FORMAT = "${:,.2f}"
PERCENTAGE_FORMAT = "{:.1f}%"
DATE_FORMAT = "%Y-%m-%d"

# Analysis Thresholds
THRESHOLDS = {
    'high_probability_lead': 70,
    'market_opportunity': 0.15,  # 15% below market value
    'high_demand_area': 100,  # searches per week
    'price_drop_significant': 0.10  # 10% price drop
}

# Natural Language Templates
RESPONSE_TEMPLATES = {
    'property_summary': """
    {property_type} at {address}
    Built in {year_built}
    {beds} beds, {baths} baths
    {sqft} square feet
    """,
    
    'market_position': """
    Current Value: {current_value}
    Market Trend: {market_trend}
    Days on Market: {dom}
    Comparable Sales: {comp_sales}
    """,
    
    'investment_potential': """
    Estimated ARV: {arv}
    Repair Costs: {repair_costs}
    Maximum Offer: {mao}
    Potential ROI: {roi}
    """,
    
    'lead_status': """
    Lead Score: {lead_score}/100
    Status: {status}
    Next Steps: {next_steps}
    Priority: {priority}
    """
}

# Data Update Schedule
UPDATE_SCHEDULE = {
    'high_demand_areas': 24,  # hours
    'market_stats': 168,      # hours (1 week)
    'property_details': 720   # hours (30 days)
}
