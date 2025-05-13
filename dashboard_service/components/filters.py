"""Filters Component

This component provides sidebar filters for the dashboard.
"""

import streamlit as st
import pandas as pd
import numpy as np

def display_filters(df):
    """Display sidebar filters and return the filtered dataframe.
    
    Args:
        df: DataFrame containing market analysis data
        
    Returns:
        Filtered DataFrame based on user selections
    """
    st.sidebar.header("Filters")
    
    # Make a copy of the dataframe to avoid modifying the original
    filtered_df = df.copy()
    
    # Check if the dataframe is empty
    if filtered_df.empty:
        st.sidebar.warning("No data available for filtering.")
        return filtered_df
    
    # Region filter
    if 'Region' in filtered_df.columns:
        regions = ['All'] + sorted(filtered_df['Region'].unique().tolist())
        selected_region = st.sidebar.selectbox("Region", regions)
        
        if selected_region != 'All':
            filtered_df = filtered_df[filtered_df['Region'] == selected_region]
    
    # Market Phase filter
    if 'Market Phase' in filtered_df.columns:
        phases = ['All'] + sorted(filtered_df['Market Phase'].unique().tolist())
        selected_phase = st.sidebar.selectbox("Market Phase", phases)
        
        if selected_phase != 'All':
            filtered_df = filtered_df[filtered_df['Market Phase'] == selected_phase]
    
    # Risk Level filter
    if 'Risk Level' in filtered_df.columns:
        risk_levels = ['All'] + sorted(filtered_df['Risk Level'].unique().tolist())
        selected_risk = st.sidebar.selectbox("Risk Level", risk_levels)
        
        if selected_risk != 'All':
            filtered_df = filtered_df[filtered_df['Risk Level'] == selected_risk]
    
    # Score range filter
    if 'Final Score' in filtered_df.columns:
        score_min = float(filtered_df['Final Score'].min())
        score_max = float(filtered_df['Final Score'].max())
        selected_score_range = st.sidebar.slider(
            "Score Range",
            min_value=score_min,
            max_value=score_max,
            value=(score_min, score_max),
            step=1.0
        )
        
        filtered_df = filtered_df[
            (filtered_df['Final Score'] >= selected_score_range[0]) &
            (filtered_df['Final Score'] <= selected_score_range[1])
        ]
    
    # Property Value range filter (if available)
    if 'Property Value' in filtered_df.columns:
        value_min = float(filtered_df['Property Value'].min())
        value_max = float(filtered_df['Property Value'].max())
        selected_value_range = st.sidebar.slider(
            "Property Value Range ($)",
            min_value=value_min,
            max_value=value_max,
            value=(value_min, value_max),
            step=10000.0
        )
        
        filtered_df = filtered_df[
            (filtered_df['Property Value'] >= selected_value_range[0]) &
            (filtered_df['Property Value'] <= selected_value_range[1])
        ]
    
    # Cap Rate range filter (if available)
    if 'Cap Rate' in filtered_df.columns:
        cap_min = float(filtered_df['Cap Rate'].min())
        cap_max = float(filtered_df['Cap Rate'].max())
        selected_cap_range = st.sidebar.slider(
            "Cap Rate Range (%)",
            min_value=cap_min,
            max_value=cap_max,
            value=(cap_min, cap_max),
            step=0.1
        )
        
        filtered_df = filtered_df[
            (filtered_df['Cap Rate'] >= selected_cap_range[0]) &
            (filtered_df['Cap Rate'] <= selected_cap_range[1])
        ]
    
    # Display filter summary
    st.sidebar.subheader("Filter Summary")
    st.sidebar.info(f"Showing {len(filtered_df)} of {len(df)} markets")
    
    # Reset filters button
    if st.sidebar.button("Reset Filters"):
        st.experimental_rerun()
    
    return filtered_df
