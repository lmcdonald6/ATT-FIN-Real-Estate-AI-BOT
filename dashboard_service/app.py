"""Real Estate AI Dashboard

A Streamlit dashboard for visualizing real estate market analysis data from Airtable.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import sys
import os

# Add the parent directory to the path to import modules from the main project
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import components
from components.map_view import display_map
from components.filters import display_filters
from components.analytics_view import display_analytics

# Import services
from services.airtable_client import get_market_analysis_data

# Set page configuration
st.set_page_config(
    page_title="Real Estate AI Dashboard",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Dashboard title and description
st.title("Real Estate AI Market Analysis Dashboard")
st.markdown("""
This dashboard provides interactive visualizations of real estate market analysis data.
Use the filters in the sidebar to customize the view.
""")

# Load data
@st.cache_data(ttl=300)  # Cache data for 5 minutes
def load_data():
    """Load market analysis data from Airtable"""
    try:
        data = get_market_analysis_data()
        if not data:
            st.error("No data found in Airtable. Please make sure your Airtable integration is configured correctly.")
            return pd.DataFrame()
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# Main function
def main():
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No data available to display. Please check your Airtable connection.")
        return
    
    # Display sidebar filters
    filtered_df = display_filters(df)
    
    # Create two columns for the dashboard layout
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Display map
        display_map(filtered_df)
    
    with col2:
        # Display key metrics
        st.subheader("Key Metrics")
        metrics_col1, metrics_col2 = st.columns(2)
        
        with metrics_col1:
            avg_score = filtered_df["Final Score"].mean() if "Final Score" in filtered_df.columns else 0
            st.metric("Average Score", f"{avg_score:.1f}")
            
            avg_ptr = filtered_df["PTR Ratio"].mean() if "PTR Ratio" in filtered_df.columns else 0
            st.metric("Average PTR Ratio", f"{avg_ptr:.2f}")
        
        with metrics_col2:
            avg_cap_rate = filtered_df["Cap Rate"].mean() if "Cap Rate" in filtered_df.columns else 0
            st.metric("Average Cap Rate", f"{avg_cap_rate:.2f}%")
            
            avg_appreciation = filtered_df["Avg Appreciation"].mean() if "Avg Appreciation" in filtered_df.columns else 0
            st.metric("Average Appreciation", f"{avg_appreciation:.1f}%")
    
    # Display analytics charts
    st.subheader("Market Analysis")
    display_analytics(filtered_df)
    
    # Display data table
    st.subheader("Market Data")
    st.dataframe(filtered_df, use_container_width=True)

# Run the dashboard
if __name__ == "__main__":
    main()
