import streamlit as st

# Page config must be the first Streamlit command
st.set_page_config(
    page_title="Real Estate AI Bot",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

import pandas as pd
import plotly.express as px
from src.services.mock_data import mock_data_service
from src.services.api_service import api_service
from src.analyzers.scoring import calculate_investment_score, get_recommendation
from src.ai_reporters.summary import generate_summary, store_results

# Custom CSS
st.markdown('''
<style>
    .stApp { background-color: #f8f9fa; }
    .main .block-container { padding-top: 2rem; }
    div[data-testid="stMetricValue"] { font-size: 24px; }
</style>
''', unsafe_allow_html=True)

# Header
st.markdown("""
<div style='background-color: #1E88E5; padding: 1rem; border-radius: 10px; color: white;'>
    <h1 style='margin: 0; font-size: 2.5rem;'>Real Estate AI Bot</h1>
    <p style='margin: 0.5rem 0 0 0; font-size: 1.1rem;'>AI-Powered Real Estate Analysis & Investment Insights</p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    # Search Section
    st.markdown("### 🔍 Property Search")
    zipcode = st.text_input("ZIP Code", value="90210", help="Enter a ZIP code to analyze")
    property_type = st.selectbox(
        "Property Type",
        ["Single Family", "Multi Family", "Commercial", "Land"]
    )
    
    # Analysis Settings
    st.markdown("### ⚙️ Analysis Settings")
    analysis_type = st.multiselect(
        "Analysis Types",
        ["Market Analysis", "Investment ROI", "Risk Assessment", "Neighborhood Score"],
        default=["Market Analysis", "Investment ROI"]
    )
    timeframe = st.slider("Time Horizon (Years)", 1, 10, 5)
    
    # AI Configuration
    st.markdown("### 🤖 AI Settings")
    ai_provider = st.selectbox(
        "AI Provider",
        ["OpenAI GPT-4", "Anthropic Claude", "Custom"],
        help="Select the AI model for analysis"
    )
    temperature = st.slider(
        "AI Temperature",
        min_value=0.0,
        max_value=1.0,
        value=0.7,
        help="Lower values = more focused, higher values = more creative"
    )
    
    # Data Sources
    st.markdown("### 📊 Data Sources")
    use_mock = st.checkbox("Use Mock Data", value=True)
    data_sources = st.multiselect(
        "Active Sources",
        ["Zillow", "Realtor.com", "Census", "FBI Crime", "Walk Score"],
        default=["Zillow", "Census", "Walk Score"],
        disabled=use_mock
    )
    temperature = st.slider("AI Temperature", 0.0, 1.0, 0.7)

# Main content
col1, col2, col3 = st.columns(3)

# Get property data
if use_mock:
    data = mock_data_service._generate_mock_property_data(zipcode)
    location = data['location']
    crime_data = data['signals']['crime']
    census_data = data['signals']['demographics']
    market_data = data['market_stats']
else:
    # Use real APIs
    try:
        location = api_service.geocode_address(zipcode)
        crime_data = api_service.get_crime_data(location['lat'], location['lng'])
        census_data = api_service.get_census_data(zipcode)
        market_data = mock_data_service.get_market_trends(zipcode)  # Fallback to mock for now
    except Exception as e:
        st.error(f"Error fetching data: {e}")
        st.stop()

# Calculate scores
investment_score, risk_data = calculate_investment_score(
    data, market_data, crime_data, census_data
)
recommendation = get_recommendation(investment_score, risk_data['risk_score'])

# Display key metrics
with col1:
    st.metric(
        "Investment Score",
        f"{investment_score}/100",
        delta="Good" if investment_score >= 70 else ("Fair" if investment_score >= 50 else "Poor")
    )
with col2:
    st.metric(
        "Risk Score",
        f"{risk_data['risk_score']}/100",
        delta="Low Risk" if risk_data['risk_score'] >= 70 else ("Medium Risk" if risk_data['risk_score'] >= 50 else "High Risk")
    )
with col3:
    st.metric(
        "Recommendation",
        recommendation,
        delta=None
    )

# Tabs for different views
tab1, tab2, tab3 = st.tabs(["Overview", "AI Analysis", "Details"])

with tab1:
    # Market signals visualization
    st.subheader("Market Signals")
    signals = {
        "Permits": data['signals']['permits']['permit_score'],
        "Demographics": data['signals']['demographics']['migration_score'],
        "Crime": data['signals']['crime']['crime_score'],
        "Transit": data['signals']['transit']['transit_score'],
        "Zoning": data['signals']['zoning']['zoning_score']
    }
    
    df = pd.DataFrame({
        'Signal': list(signals.keys()),
        'Score': list(signals.values())
    })
    
    fig = px.bar(df, x='Signal', y='Score',
                 title="Signal Analysis",
                 color='Score',
                 color_continuous_scale='viridis',
                 range_y=[0, 100])
    st.plotly_chart(fig, use_container_width=True)
    
    # Market stats
    st.subheader("Market Statistics")
    col1, col2 = st.columns(2)
    with col1:
        st.write("📈 Price Trends")
        st.write(f"Median Home Price: ${data['market_stats']['median_home_price']:,}")
        st.write(f"1Y Price Growth: {data['market_stats']['price_growth_1y']}%")
    with col2:
        st.write("🏘️ Market Health")
        st.write(f"Rental Vacancy: {data['market_stats']['rental_vacancy']}%")
        st.write(f"Average Cap Rate: {data['market_stats']['cap_rate_avg']}%")

with tab2:
    st.subheader("AI Analysis")
    
    # Generate and display AI summary
    summary = generate_summary(
        data,
        {
            "investment_score": investment_score,
            "risk_score": risk_data["risk_score"],
            "risk_factors": risk_data["risk_factors"],
            "component_scores": risk_data["component_scores"]
        },
        recommendation
    )
    
    st.markdown(summary)
    
    # Save results button
    if st.button("💾 Save Analysis"):
        try:
            store_results(data, risk_data, recommendation, use_airtable=False)
            st.success("Analysis saved successfully!")
        except Exception as e:
            st.error(f"Error saving analysis: {e}")

with tab3:
    st.subheader("Detailed Analysis")
    
    # Permits
    st.write("### Building Permits")
    permits = data['signals']['permits']
    st.write(f"- Residential Permits: {permits['residential_permits']}")
    st.write(f"- Commercial Permits: {permits['commercial_permits']}")
    st.write(f"- Renovation Permits: {permits['renovation_permits']}")
    
    # Demographics
    st.write("### Demographics")
    demo = data['signals']['demographics']
    st.write(f"- Population Growth: {demo['population_growth']}%")
    st.write(f"- Median Income: ${demo['median_income']:,}")
    st.write(f"- Employment Rate: {demo['employment_rate']*100:.1f}%")
    
    # Location
    st.write("### Location")
    st.write(f"- City: {data['location']['city']}")
    st.write(f"- State: {data['location']['state']}")
    st.write(f"- Coordinates: ({data['location']['lat']}, {data['location']['lng']})")

# Footer
st.markdown("---")
st.markdown("*This is a demo version using mock data. For real data, please configure API keys in settings.*")
