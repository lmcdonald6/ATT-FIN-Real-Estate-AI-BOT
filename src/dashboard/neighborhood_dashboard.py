#!/usr/bin/env python3
"""
Neighborhood Intelligence Dashboard

A Streamlit dashboard for visualizing neighborhood analysis results.
"""

import os
import sys
import pandas as pd
from typing import List, Dict, Any

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Streamlit imports - will fail if not installed
try:
    import streamlit as st
    import plotly.express as px
    import plotly.graph_objects as go
except ImportError:
    print("Streamlit or Plotly not installed. Run 'pip install streamlit plotly'")
    sys.exit(1)

from src.integration.combine_market_and_sentiment import combine_analysis

# Default ZIP codes to analyze
DEFAULT_ZIPS = ["30318", "11238", "90210", "33101", "60614", "75201"]

# Page configuration
st.set_page_config(
    page_title="Neighborhood Intelligence Dashboard", 
    page_icon="ud83cudfd9ufe0f",
    layout="wide"
)

# Title and description
st.title("ud83cudfd9ufe0f Neighborhood Intelligence Dashboard")
st.markdown("""
This dashboard provides real-time analysis of neighborhoods using market data and social sentiment.
Select a ZIP code to view detailed analysis or compare multiple neighborhoods.
""")

# Sidebar
st.sidebar.header("Analysis Options")

# Analysis mode selection
analysis_mode = st.sidebar.radio(
    "Choose analysis mode:",
    ["Single ZIP Analysis", "Multi-ZIP Comparison"]
)

# Function to load and cache analysis results
@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_analysis(zip_code: str) -> Dict[str, Any]:
    """Get analysis results for a ZIP code with caching."""
    return combine_analysis(zip_code)


@st.cache_data(ttl=3600)  # Cache for 1 hour
def get_multiple_analyses(zip_codes: List[str]) -> List[Dict[str, Any]]:
    """Get analysis results for multiple ZIP codes with caching."""
    return [combine_analysis(zip_code) for zip_code in zip_codes]


def display_single_zip_analysis(zip_code: str) -> None:
    """Display detailed analysis for a single ZIP code."""
    st.subheader(f"ud83dudccd ZIP: {zip_code}")
    
    with st.spinner(f"Analyzing ZIP {zip_code}..."):
        result = get_analysis(zip_code)
    
    # Create columns for metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("ud83cudfe1 Market Score", result["market_score"])
        st.metric("ud83dudcc8 Trend Score", result["trend_score"])
        st.metric("ud83dudcca Economic Score", result["econ_score"])
    
    with col2:
        st.metric("ud83eudd1d Reputation Score", result["reputation_score"])
        st.text(f"Buzz Source: {result['buzz_source']}")
    
    # Display summaries
    st.subheader("ud83eudde0 Summary")
    st.markdown(f"**Market:** {result['market_summary']}")
    st.markdown(f"**Buzz:** {result['buzz_summary']}")
    
    # Additional details in an expander
    with st.expander("View Raw Data"):
        # Filter out internal fields (starting with underscore)
        filtered_result = {k: v for k, v in result.items() if not k.startswith('_')}
        st.json(filtered_result)


def display_multi_zip_comparison(zip_codes: List[str]) -> None:
    """Display comparison of multiple ZIP codes."""
    st.subheader(f"ud83dudd04 Comparing {len(zip_codes)} ZIP Codes")
    
    with st.spinner("Analyzing multiple ZIP codes..."):
        results = get_multiple_analyses(zip_codes)
    
    # Convert to DataFrame for easier manipulation
    df = pd.DataFrame(results)
    
    # Create a bar chart comparing key metrics
    metrics = [
        ('market_score', 'Market Score'),
        ('trend_score', 'Trend Score'),
        ('econ_score', 'Economic Score'),
        ('reputation_score', 'Reputation Score')
    ]
    
    # Create the comparison chart
    fig = go.Figure()
    
    for zip_code, result in zip(df['zip'], results):
        values = [result.get(metric, 0) for metric, _ in metrics]
        fig.add_trace(go.Bar(
            x=[label for _, label in metrics],
            y=values,
            name=f'ZIP {zip_code}'
        ))
    
    fig.update_layout(
        title="ZIP Code Comparison",
        yaxis_title="Score (0-100)",
        barmode='group',
        yaxis=dict(range=[0, 100])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Create a table with all results
    st.subheader("ud83dudcca Comparison Table")
    
    # Select and rename columns for display
    display_cols = {
        'zip': 'ZIP Code',
        'market_score': 'Market Score',
        'trend_score': 'Trend Score',
        'econ_score': 'Economic Score',
        'reputation_score': 'Reputation Score'
    }
    
    display_df = df[display_cols.keys()].rename(columns=display_cols)
    st.dataframe(display_df, use_container_width=True)
    
    # Show summaries in expanders
    st.subheader("ud83dudcdd Neighborhood Summaries")
    
    for result in results:
        with st.expander(f"ZIP {result['zip']}"):
            st.markdown(f"**Market:** {result['market_summary']}")
            st.markdown(f"**Buzz:** {result['buzz_summary']}")


# Main content based on selected mode
if analysis_mode == "Single ZIP Analysis":
    # ZIP code selection for single analysis
    selected_zip = st.sidebar.selectbox("Choose a ZIP code to analyze:", DEFAULT_ZIPS)
    
    # Option to enter a custom ZIP
    use_custom_zip = st.sidebar.checkbox("Enter a custom ZIP code")
    if use_custom_zip:
        custom_zip = st.sidebar.text_input("Enter ZIP code:", "")
        if custom_zip.strip() and custom_zip.isdigit() and len(custom_zip) == 5:
            selected_zip = custom_zip
        else:
            st.sidebar.warning("Please enter a valid 5-digit ZIP code")
    
    # Display the analysis
    if selected_zip:
        display_single_zip_analysis(selected_zip)

else:  # Multi-ZIP Comparison
    # ZIP code selection for comparison
    selected_zips = st.sidebar.multiselect(
        "Select ZIP codes to compare:",
        DEFAULT_ZIPS,
        default=DEFAULT_ZIPS[:3]
    )
    
    # Option to add a custom ZIP
    use_custom_zip = st.sidebar.checkbox("Add a custom ZIP code")
    if use_custom_zip:
        custom_zip = st.sidebar.text_input("Enter ZIP code:", "")
        if st.sidebar.button("Add to Comparison") and custom_zip.strip() and custom_zip.isdigit() and len(custom_zip) == 5:
            if custom_zip not in selected_zips:
                selected_zips.append(custom_zip)
    
    # Display the comparison
    if selected_zips:
        display_multi_zip_comparison(selected_zips)
    else:
        st.warning("Please select at least one ZIP code to analyze")

# Footer
st.markdown("---")
st.caption("Powered by ATT-FIN Real Estate AI Bot")
