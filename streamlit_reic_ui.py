#!/usr/bin/env python3
"""
Streamlit UI for Real Estate Intelligence Core (REIC)

This module provides a Streamlit-based user interface for interacting with
the Real Estate Intelligence Core, allowing users to analyze real estate data,
view insights, and export reports.
"""

import os
import sys
import json
import logging
import base64
from datetime import datetime
from typing import Dict, List, Any, Optional

import streamlit as st
from PIL import Image

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.abspath(__file__))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import inference components
from src.inference.inference_layer_manager import InferenceLayerManager

# Import export components
from src.utils.simple_export import simple_export


# ----------------------------
# Page Configuration
# ----------------------------
st.set_page_config(
    page_title="Real Estate Intelligence Core",
    page_icon="🏘️",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ----------------------------
# Helper Functions
# ----------------------------
def get_file_download_link(file_path, link_text):
    """Generate a download link for a file."""
    with open(file_path, "rb") as f:
        data = f.read()
    b64 = base64.b64encode(data).decode()
    extension = os.path.splitext(file_path)[1]
    
    if extension == ".pdf":
        mime_type = "application/pdf"
    elif extension == ".csv":
        mime_type = "text/csv"
    elif extension == ".json":
        mime_type = "application/json"
    else:
        mime_type = "text/plain"
    
    href = f'<a href="data:{mime_type};base64,{b64}" download="{os.path.basename(file_path)}">{link_text}</a>'
    return href


# ----------------------------
# Property Media Carousel
# ----------------------------
def property_media(images: list):
    """Display property images in a carousel."""
    st.subheader("🏡 Property Media")
    if not images:
        st.warning("No media available.")
        return

    for i, img_path in enumerate(images):
        try:
            st.image(img_path, caption=f"Image {i+1}", use_column_width=True)
        except Exception as e:
            st.error(f"Error loading image: {e}")


# ----------------------------
# Mortgage Calculator Module
# ----------------------------
def mortgage_calculator():
    """Interactive mortgage calculator."""
    st.subheader("📊 Mortgage Calculator")

    col1, col2 = st.columns(2)
    
    with col1:
        price = st.number_input("Home Price ($)", value=500000, min_value=50000, step=10000)
        down_payment = st.number_input("Down Payment ($)", value=100000, min_value=0, max_value=int(price), step=5000)
    
    with col2:
        interest_rate = st.slider("Interest Rate (%)", 2.5, 10.0, 6.5, 0.1)
        loan_term = st.selectbox("Loan Term (years)", [15, 20, 30], index=2)

    loan_amount = price - down_payment
    monthly_rate = interest_rate / 100 / 12
    payments = loan_term * 12

    monthly_payment = (loan_amount * monthly_rate) / (1 - (1 + monthly_rate)**-payments)
    total_payment = monthly_payment * payments
    total_interest = total_payment - loan_amount

    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    col1.metric("Monthly Payment", f"${monthly_payment:,.2f}")
    col2.metric("Total Interest", f"${total_interest:,.2f}")
    col3.metric("Total Cost", f"${total_payment:,.2f}")


# ----------------------------
# School Info Module
# ----------------------------
def school_info(zip_code: str):
    """Display local school information for a ZIP code."""
    st.subheader("🏫 Local School Ratings")
    
    # In a real implementation, this would fetch data from an API
    # For now, we'll use mock data based on the ZIP code
    mock_schools = [
        {"name": f"{zip_code} Elementary", "rating": 8, "distance": "1.2 mi"},
        {"name": f"{zip_code} Middle School", "rating": 7, "distance": "1.4 mi"},
        {"name": f"{zip_code} High School", "rating": 9, "distance": "2.1 mi"}
    ]
    
    for school in mock_schools:
        col1, col2, col3 = st.columns([3, 1, 1])
        col1.markdown(f"**{school['name']}**")
        col2.markdown(f"Rating: {school['rating']}/10")
        col3.markdown(f"{school['distance']}")


# ----------------------------
# Market Analysis Module
# ----------------------------
def market_analysis(zip_code: str):
    """Display market analysis for a ZIP code using the inference layer manager."""
    st.subheader("📈 Market Analysis")
    
    # Initialize the inference layer manager
    manager = InferenceLayerManager()
    
    # Define queries for different temporal perspectives
    queries = {
        "Past": f"What were the historical trends for ZIP code {zip_code} over the past 5 years?",
        "Present": f"What is the current sentiment for ZIP code {zip_code}?",
        "Future": f"What is the forecast for residential real estate in ZIP code {zip_code} over the next 12 months?"
    }
    
    # Create tabs for different temporal perspectives
    tabs = st.tabs(["Past", "Present", "Future", "Combined"])
    
    # Process each query and display results
    results = {}
    for i, (perspective, query) in enumerate(queries.items()):
        with tabs[i]:
            with st.spinner(f"Analyzing {perspective.lower()} market data..."):
                # Process the query
                result = manager.process_query(query, {"zip_codes": [zip_code]})
                results[perspective] = result
                
                # Display insights
                insights = result.get("insights", [])
                if insights:
                    for insight in insights:
                        st.info(insight.get("insight", ""))
                else:
                    st.warning(f"No {perspective.lower()} insights available for ZIP code {zip_code}.")
                
                # Display scores if available
                if "results" in result and zip_code in result["results"]:
                    zip_result = result["results"][zip_code]
                    scores = {}
                    for score_name in ["market_score", "reputation_score", "trend_score", "econ_score"]:
                        if score_name in zip_result:
                            scores[score_name.replace("_", " ").title()] = zip_result.get(score_name, 0)
                    
                    if scores:
                        st.markdown("### Scores")
                        cols = st.columns(len(scores))
                        for i, (label, score) in enumerate(scores.items()):
                            cols[i].metric(label, f"{score}/100")
    
    # Combined analysis
    with tabs[3]:
        with st.spinner("Generating combined analysis..."):
            # Process a combined query
            combined_query = f"Compare the historical, current, and future trends for ZIP code {zip_code}."
            combined_result = manager.process_query(combined_query, {"zip_codes": [zip_code]})
            results["Combined"] = combined_result
            
            # Display summary
            if "summary" in combined_result:
                st.markdown("### Summary")
                st.write(combined_result["summary"])
            
            # Display insights
            insights = combined_result.get("insights", [])
            if insights:
                st.markdown("### Key Insights")
                for insight in insights:
                    st.info(insight.get("insight", ""))
            else:
                st.warning(f"No combined insights available for ZIP code {zip_code}.")
    
    return results


# ----------------------------
# Export Module
# ----------------------------
def export_analysis(zip_code: str, results: Dict[str, Any]):
    """Export analysis results in various formats."""
    st.subheader("📄 Export Analysis")
    
    # Use the combined results if available, otherwise use the present results
    if "Combined" in results:
        result = results["Combined"]
    elif "Present" in results:
        result = results["Present"]
    else:
        result = next(iter(results.values()))
    
    # Prepare export data
    export_data = {
        "zip": zip_code,
        "query": f"Real Estate Analysis for ZIP code {zip_code}",
        "timestamp": datetime.now().isoformat(),
        "summary": result.get("summary", f"Analysis summary for ZIP code {zip_code}")
    }
    
    # Extract scores
    scores = {}
    if "results" in result and zip_code in result["results"]:
        zip_result = result["results"][zip_code]
        for score_name in ["market_score", "reputation_score", "trend_score", "econ_score"]:
            if score_name in zip_result:
                scores[score_name.replace("_", " ").title()] = zip_result.get(score_name, 0)
    
    # Add insights as scores if no scores are available
    if not scores and "insights" in result:
        for i, insight in enumerate(result.get("insights", [])[:3]):
            if "metric" in insight and "value" in insight:
                scores[f"{insight['metric'].replace('_', ' ').title()}"] = insight["value"]
    
    # Add scores to export data
    export_data["scores"] = scores
    
    # Create output directory
    output_dir = os.path.join(sys_path, "output")
    os.makedirs(output_dir, exist_ok=True)
    
    # Export format selection
    format_type = st.selectbox("Select Export Format", ["PDF", "Text", "CSV", "JSON"], index=0)
    
    if st.button("Generate Report"):
        with st.spinner(f"Generating {format_type} report..."):
            # Export the data
            export_path = simple_export(export_data, format_type.lower(), output_dir)
            
            # Check if export was successful
            if export_path and os.path.exists(export_path):
                st.success(f"{format_type} report generated successfully!")
                st.markdown(get_file_download_link(export_path, f"Download {format_type} Report"), unsafe_allow_html=True)
            else:
                st.error(f"Failed to generate {format_type} report.")


# ----------------------------
# Save/Favorite Button
# ----------------------------
def save_listing_button():
    """Button to save/favorite a listing."""
    if st.button("⭐ Save This Analysis"):
        st.success("Analysis saved to your favorites")


# ----------------------------
# Main Application
# ----------------------------
def main():
    """Main Streamlit application."""
    # Sidebar
    st.sidebar.image("https://via.placeholder.com/150x150.png?text=REIC", width=150)
    st.sidebar.title("Real Estate Intelligence Core")
    st.sidebar.markdown("---")
    
    # ZIP code input
    zip_code = st.sidebar.text_input("Enter ZIP Code", value="90210")
    
    # Temporal focus
    st.sidebar.markdown("### Temporal Focus")
    past_weight = st.sidebar.slider("Historical Data", 0, 10, 5)
    present_weight = st.sidebar.slider("Current Market", 0, 10, 5)
    future_weight = st.sidebar.slider("Future Forecast", 0, 10, 5)
    
    # Advanced options
    st.sidebar.markdown("### Advanced Options")
    show_advanced = st.sidebar.checkbox("Show Advanced Options")
    
    if show_advanced:
        st.sidebar.selectbox("Analysis Model", ["Standard", "Premium", "Enterprise"], index=0)
        st.sidebar.multiselect("Data Sources", ["MLS", "Public Records", "Census", "Social Media"], default=["MLS", "Public Records"])
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 Real Estate Intelligence Core")
    
    # Main content
    st.title("🏘️ Real Estate Intelligence Analysis")
    st.markdown(f"### Analysis for ZIP Code: {zip_code}")
    
    # Run analysis when button is clicked
    if st.button("Run Analysis") or "results" in st.session_state:
        # Store results in session state if not already present
        if "results" not in st.session_state:
            with st.spinner("Running comprehensive analysis..."):
                results = market_analysis(zip_code)
                st.session_state.results = results
                st.session_state.zip_code = zip_code
        elif st.session_state.zip_code != zip_code:
            # Update results if ZIP code has changed
            with st.spinner("Running comprehensive analysis..."):
                results = market_analysis(zip_code)
                st.session_state.results = results
                st.session_state.zip_code = zip_code
        else:
            # Use cached results
            results = st.session_state.results
        
        # Display tabs for different modules
        tab1, tab2, tab3, tab4 = st.tabs(["Market Analysis", "Property Details", "Mortgage Calculator", "Export"])
        
        with tab1:
            # Market analysis is already displayed above
            pass
        
        with tab2:
            col1, col2 = st.columns([2, 1])
            
            with col1:
                # Mock property images
                property_media(["https://via.placeholder.com/800x600.png?text=Property+Image+1", 
                               "https://via.placeholder.com/800x600.png?text=Property+Image+2"])
            
            with col2:
                # School information
                school_info(zip_code)
                
                # Save button
                save_listing_button()
        
        with tab3:
            mortgage_calculator()
        
        with tab4:
            export_analysis(zip_code, results)
    else:
        st.info("Click 'Run Analysis' to generate a comprehensive real estate intelligence report.")


# Run the application
if __name__ == "__main__":
    main()
