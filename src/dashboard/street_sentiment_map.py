#!/usr/bin/env python3
"""
Street-Level Sentiment Map Dashboard

This Streamlit dashboard visualizes street-level sentiment analysis results
on an interactive map, allowing users to explore sentiment patterns across
different streets and neighborhoods.
"""

import os
import sys
import json
import pandas as pd
from typing import Dict, List, Any, Optional, Tuple

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import required libraries - will fail if not installed
try:
    import streamlit as st
    import folium
    from folium.plugins import HeatMap, MarkerCluster
    from streamlit_folium import st_folium
    import plotly.express as px
except ImportError:
    print("Required packages not installed. Run 'pip install streamlit folium streamlit-folium plotly'")
    sys.exit(1)

# Import our street sentiment analyzer
from src.analysis.street_sentiment_analyzer import analyze_street_sentiment, analyze_multiple_streets

# Import ZIP to metro mapping
from src.utils.zip_to_metro_mapping import get_metro_for_zip, get_data_sources_for_zip

# Sample street data with coordinates
# In a production environment, this would come from a database
STREET_DATA = [
    {"street": "Edgewood Ave", "zip": "30318", "lat": 33.7550, "lon": -84.3735, "metro": "atlanta"},
    {"street": "Auburn Ave", "zip": "30312", "lat": 33.7558, "lon": -84.3775, "metro": "atlanta"},
    {"street": "Ponce de Leon Ave", "zip": "30308", "lat": 33.7726, "lon": -84.3774, "metro": "atlanta"},
    {"street": "Bedford Ave", "zip": "11238", "lat": 40.6781, "lon": -73.9441, "metro": "nyc"},
    {"street": "Atlantic Ave", "zip": "11217", "lat": 40.6845, "lon": -73.9799, "metro": "nyc"},
    {"street": "Valencia St", "zip": "94110", "lat": 37.7583, "lon": -122.4212, "metro": "sf"},
    {"street": "Mission St", "zip": "94110", "lat": 37.7598, "lon": -122.4194, "metro": "sf"},
    {"street": "Rodeo Dr", "zip": "90210", "lat": 34.0771, "lon": -118.4011, "metro": "la"},
    {"street": "Melrose Ave", "zip": "90069", "lat": 34.0841, "lon": -118.3700, "metro": "la"}
]

# Cache for sentiment results to avoid repeated API calls
SENTIMENT_CACHE = {}


def get_street_sentiment(street: str, zip_code: str, force_refresh: bool = False) -> Dict[str, Any]:
    """
    Get sentiment analysis for a street, using cache if available.
    
    Args:
        street: Street name
        zip_code: ZIP code
        force_refresh: Whether to force a refresh of the data
        
    Returns:
        Sentiment analysis result
    """
    cache_key = f"{street}|{zip_code}"
    
    # Return cached result if available and not forcing refresh
    if not force_refresh and cache_key in SENTIMENT_CACHE:
        return SENTIMENT_CACHE[cache_key]
    
    # Get fresh analysis
    result = analyze_street_sentiment(street, zip_code)
    
    # Cache the result
    SENTIMENT_CACHE[cache_key] = result
    
    return result


def create_sentiment_map(streets_data: List[Dict[str, Any]], center: List[float] = None) -> folium.Map:
    """
    Create a folium map with sentiment markers for each street.
    
    Args:
        streets_data: List of street data dictionaries
        center: Center coordinates for the map [lat, lon]
        
    Returns:
        Folium map object
    """
    # Determine map center if not provided
    if not center and streets_data:
        # Use the average of all coordinates
        lats = [s["lat"] for s in streets_data]
        lons = [s["lon"] for s in streets_data]
        center = [sum(lats) / len(lats), sum(lons) / len(lons)]
    elif not center:
        # Default to Atlanta
        center = [33.76, -84.38]
    
    # Create the map
    m = folium.Map(location=center, zoom_start=12, tiles="CartoDB positron")
    
    # Create a marker cluster group
    marker_cluster = MarkerCluster().add_to(m)
    
    # Add markers for each street
    for street_info in streets_data:
        # Get sentiment analysis
        result = get_street_sentiment(street_info["street"], street_info["zip"])
        score = result.get("score", 0) * 100  # Convert to 0-100 scale
        
        # Determine marker color based on score
        color = "green" if score >= 70 else "orange" if score >= 50 else "red"
        
        # Create popup content
        popup_html = f"""
        <div style="width: 250px">
            <h4>{street_info['street']} ({street_info['zip']})</h4>
            <p><b>Score:</b> {score:.1f}/100</p>
            <p><b>Metro:</b> {result.get('metro', 'Unknown').title()}</p>
            <p><b>Platform:</b> {result.get('platform', 'Unknown')}</p>
            <p><b>Summary:</b> {result.get('summary', 'No summary available')[:150]}...</p>
        </div>
        """
        
        # Add marker
        folium.CircleMarker(
            location=[street_info["lat"], street_info["lon"]],
            radius=8,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{street_info['street']} - {score:.1f}/100",
            color=color,
            fill=True,
            fill_opacity=0.7
        ).add_to(marker_cluster)
    
    # Add heatmap layer if there are enough points
    if len(streets_data) >= 3:
        heat_data = [
            [s["lat"], s["lon"], get_street_sentiment(s["street"], s["zip"]).get("score", 0) * 100]
            for s in streets_data
        ]
        HeatMap(heat_data, radius=15, blur=10, gradient={0.4: 'blue', 0.65: 'lime', 0.8: 'yellow', 1: 'red'}).add_to(m)
    
    # Add layer control
    folium.LayerControl().add_to(m)
    
    return m


def main():
    """
    Main function to run the Streamlit dashboard.
    """
    # Page configuration
    st.set_page_config(
        page_title="Street-Level Sentiment Map",
        page_icon="ud83dudccd",
        layout="wide"
    )
    
    # Title and description
    st.title("ud83dudccd Street-Level Sentiment Map")
    st.markdown("""
    This dashboard visualizes sentiment analysis results for specific streets across different neighborhoods.
    Select a metropolitan area to view streets in that region, or analyze sentiment for a specific street.
    """)
    
    # Sidebar
    st.sidebar.header("Analysis Options")
    
    # Metro selection
    metros = sorted(list(set(s["metro"] for s in STREET_DATA if "metro" in s)))
    selected_metro = st.sidebar.selectbox(
        "Select a Metropolitan Area",
        options=["All"] + metros,
        index=0
    )
    
    # Filter streets by selected metro
    if selected_metro == "All":
        filtered_streets = STREET_DATA
    else:
        filtered_streets = [s for s in STREET_DATA if s.get("metro") == selected_metro]
    
    # Street selection for detailed analysis
    st.sidebar.markdown("---")
    st.sidebar.header("Street Analysis")
    
    street_options = [f"{s['street']} ({s['zip']})" for s in filtered_streets]
    selected_street = st.sidebar.selectbox("Select a Street", street_options)
    
    platform_options = ["Auto", "Reddit", "Twitter", "Facebook", "Yelp", "Nextdoor", "TikTok", "YouTube"]
    selected_platform = st.sidebar.selectbox("Data Source", platform_options)
    
    run_button = st.sidebar.button("ud83dudd04 Analyze Sentiment")
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["ud83cudfd9 Map View", "ud83dudcca Street Analysis", "ud83dudcc8 Comparison"])
    
    # Tab 1: Map View
    with tab1:
        # Create and display the map
        if filtered_streets:
            if selected_metro == "All":
                # For "All", use a US-centered view
                map_center = [39.8283, -98.5795]
                zoom_start = 4
            else:
                # For specific metro, calculate center from streets
                lats = [s["lat"] for s in filtered_streets]
                lons = [s["lon"] for s in filtered_streets]
                map_center = [sum(lats) / len(lats), sum(lons) / len(lons)]
                zoom_start = 12
            
            m = create_sentiment_map(filtered_streets, map_center)
            st_map = st_folium(m, width="100%", height=600)
        else:
            st.warning("No streets available for the selected filters.")
    
    # Tab 2: Street Analysis
    with tab2:
        if run_button and selected_street:
            street_name, zip_code = selected_street.split(" (")
            zip_code = zip_code.strip(")")
            
            # Determine platform to use
            platform = None if selected_platform == "Auto" else selected_platform
            
            with st.spinner(f"Analyzing sentiment for {street_name} in {zip_code}..."):
                # Force refresh to get latest data
                live_result = analyze_street_sentiment(street_name, zip_code, platform)
            
            # Display results
            st.subheader(f"ud83dudcf0 Sentiment Analysis: {street_name} [{zip_code}]")
            
            # Create columns for metrics
            col1, col2, col3 = st.columns(3)
            
            with col1:
                score = live_result.get("score", 0) * 100
                st.metric("Sentiment Score", f"{score:.1f}/100")
            
            with col2:
                st.metric("Metro Area", live_result.get("metro", "Unknown").title())
            
            with col3:
                st.metric("Data Source", live_result.get("platform", "Unknown"))
            
            # Display summary
            st.markdown("### Summary")
            st.markdown(live_result.get("summary", "No summary available"))
            
            # Display sample posts
            st.markdown("### Sample Posts")
            posts = live_result.get("posts", [])
            
            if posts:
                for i, post in enumerate(posts):
                    with st.expander(f"Post {i+1}"):
                        if isinstance(post, dict):
                            # Handle structured post data
                            st.markdown(f"**Title:** {post.get('title', 'No title')}")
                            st.markdown(f"**Date:** {post.get('date', 'Unknown date')}")
                            st.markdown(f"**Content:** {post.get('content', 'No content')}")
                        else:
                            # Handle string post data
                            st.markdown(post)
            else:
                st.info("No posts available.")
            
            # Show recommended sources
            st.markdown("### Recommended Data Sources")
            sources = live_result.get("recommended_platforms", [])
            if sources:
                st.write(", ".join(sources))
            else:
                st.info("No recommended sources available.")
    
    # Tab 3: Comparison
    with tab3:
        st.subheader("ud83dudcca Street Sentiment Comparison")
        
        # Get data for all streets in the filtered set
        comparison_data = []
        
        for street_info in filtered_streets:
            result = get_street_sentiment(street_info["street"], street_info["zip"])
            comparison_data.append({
                "Street": street_info["street"],
                "ZIP": street_info["zip"],
                "Metro": result.get("metro", "Unknown").title(),
                "Score": result.get("score", 0) * 100,
                "Platform": result.get("platform", "Unknown")
            })
        
        # Convert to DataFrame
        if comparison_data:
            df = pd.DataFrame(comparison_data)
            
            # Create bar chart
            fig = px.bar(
                df,
                x="Street",
                y="Score",
                color="Metro",
                hover_data=["ZIP", "Platform"],
                title="Sentiment Scores by Street",
                labels={"Score": "Sentiment Score (0-100)"},
                height=500
            )
            
            st.plotly_chart(fig, use_container_width=True)
            
            # Display data table
            st.markdown("### Data Table")
            st.dataframe(df, use_container_width=True)
            
            # Metro averages
            st.markdown("### Metro Averages")
            metro_avg = df.groupby("Metro")["Score"].mean().reset_index()
            metro_avg.columns = ["Metro", "Average Score"]
            
            # Create metro comparison chart
            fig2 = px.bar(
                metro_avg,
                x="Metro",
                y="Average Score",
                color="Metro",
                title="Average Sentiment Score by Metro",
                labels={"Average Score": "Average Sentiment Score (0-100)"},
                height=400
            )
            
            st.plotly_chart(fig2, use_container_width=True)
        else:
            st.warning("No data available for comparison.")


if __name__ == "__main__":
    main()
