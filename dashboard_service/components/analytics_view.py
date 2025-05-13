"""Analytics View Component

This component displays analytics charts and visualizations for market analysis data.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def display_analytics(df):
    """Display analytics charts for market analysis data.
    
    Args:
        df: DataFrame containing market analysis data
    """
    if df.empty:
        st.warning("No data available for analytics.")
        return
    
    # Create tabs for different analytics views
    tab1, tab2, tab3 = st.tabs(["Market Comparison", "Risk Analysis", "Investment Metrics"])
    
    with tab1:
        display_market_comparison(df)
    
    with tab2:
        display_risk_analysis(df)
    
    with tab3:
        display_investment_metrics(df)

def display_market_comparison(df):
    """Display market comparison charts.
    
    Args:
        df: DataFrame containing market analysis data
    """
    # Check if we have the necessary columns
    if 'Region' not in df.columns:
        st.warning("Region data is missing. Cannot display market comparison.")
        return
    
    # Determine which score column to use
    score_column = 'Final Score' if 'Final Score' in df.columns else ('Score' if 'Score' in df.columns else None)
    
    if score_column:
        # Sort by score
        sorted_df = df.sort_values(by=score_column, ascending=False)
        
        # Create a horizontal bar chart of scores by region
        fig = px.bar(
            sorted_df,
            y='Region',
            x=score_column,
            orientation='h',
            title=f'Market Score by Region',
            color=score_column,
            color_continuous_scale=px.colors.sequential.Viridis,
            height=400
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title='Score',
            yaxis_title='Region',
            yaxis={'categoryorder':'total ascending'},
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    
    # Create a comparison chart for economic and trend scores if available
    if 'Economic Score' in df.columns and 'Trend Score' in df.columns:
        # Sort by economic score
        sorted_df = df.sort_values(by='Economic Score', ascending=False)
        
        # Create a grouped bar chart
        fig = go.Figure()
        
        # Add economic score bars
        fig.add_trace(go.Bar(
            y=sorted_df['Region'],
            x=sorted_df['Economic Score'],
            name='Economic Score',
            orientation='h',
            marker=dict(color='rgba(58, 71, 80, 0.8)')
        ))
        
        # Add trend score bars
        fig.add_trace(go.Bar(
            y=sorted_df['Region'],
            x=sorted_df['Trend Score'],
            name='Trend Score',
            orientation='h',
            marker=dict(color='rgba(246, 78, 139, 0.8)')
        ))
        
        # Update layout
        fig.update_layout(
            title='Economic vs Trend Scores by Region',
            barmode='group',
            yaxis={'categoryorder':'array', 'categoryarray':sorted_df['Region']},
            margin=dict(l=0, r=0, t=40, b=0),
            height=400
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)

def display_risk_analysis(df):
    """Display risk analysis charts.
    
    Args:
        df: DataFrame containing market analysis data
    """
    # Check if we have the necessary columns
    if 'Risk Level' not in df.columns:
        st.warning("Risk data is missing. Cannot display risk analysis.")
        return
    
    # Create a pie chart of risk levels
    risk_counts = df['Risk Level'].value_counts().reset_index()
    risk_counts.columns = ['Risk Level', 'Count']
    
    fig = px.pie(
        risk_counts,
        values='Count',
        names='Risk Level',
        title='Distribution of Risk Levels',
        color_discrete_sequence=px.colors.sequential.RdBu,
        hole=0.4
    )
    
    # Update layout
    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0)
    )
    
    # Display the chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Create a scatter plot of risk vs return if we have the necessary columns
    if 'Cap Rate' in df.columns and 'Risk Level' in df.columns:
        # Create a numeric risk level for plotting
        risk_mapping = {
            'Low': 1,
            'Moderate': 2,
            'High': 3,
            'Very High': 4
        }
        
        # Create a copy to avoid modifying the original
        plot_df = df.copy()
        
        # Map risk levels to numeric values if possible
        if all(risk in risk_mapping for risk in plot_df['Risk Level'].unique()):
            plot_df['Risk Numeric'] = plot_df['Risk Level'].map(risk_mapping)
            
            # Create scatter plot
            fig = px.scatter(
                plot_df,
                x='Risk Numeric',
                y='Cap Rate',
                color='Region',
                size='Property Value' if 'Property Value' in plot_df.columns else None,
                hover_name='Region',
                title='Risk vs Return Analysis',
                labels={'Risk Numeric': 'Risk Level', 'Cap Rate': 'Cap Rate (%)'},
                height=400
            )
            
            # Update x-axis to show original risk levels
            fig.update_layout(
                xaxis=dict(
                    tickmode='array',
                    tickvals=list(risk_mapping.values()),
                    ticktext=list(risk_mapping.keys()),
                    title='Risk Level'
                ),
                margin=dict(l=0, r=0, t=40, b=0)
            )
            
            # Display the chart
            st.plotly_chart(fig, use_container_width=True)

def display_investment_metrics(df):
    """Display investment metrics charts.
    
    Args:
        df: DataFrame containing market analysis data
    """
    # Check if we have the necessary columns for PTR ratio analysis
    if 'PTR Ratio' in df.columns and 'Region' in df.columns:
        # Sort by PTR ratio
        sorted_df = df.sort_values(by='PTR Ratio', ascending=False)
        
        # Create a bar chart of PTR ratios
        fig = px.bar(
            sorted_df,
            y='Region',
            x='PTR Ratio',
            orientation='h',
            title='Price-to-Rent Ratio by Region',
            color='PTR Ratio',
            color_continuous_scale=px.colors.sequential.Bluered_r,  # Higher is worse for PTR
            height=400
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title='Price-to-Rent Ratio',
            yaxis_title='Region',
            yaxis={'categoryorder':'total ascending'},
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    
    # Check if we have the necessary columns for appreciation analysis
    if 'Avg Appreciation' in df.columns and 'Region' in df.columns:
        # Sort by appreciation
        sorted_df = df.sort_values(by='Avg Appreciation', ascending=False)
        
        # Create a bar chart of appreciation rates
        fig = px.bar(
            sorted_df,
            y='Region',
            x='Avg Appreciation',
            orientation='h',
            title='Average Appreciation Rate by Region (%)',
            color='Avg Appreciation',
            color_continuous_scale=px.colors.sequential.Viridis,
            height=400
        )
        
        # Update layout
        fig.update_layout(
            xaxis_title='Average Appreciation (%)',
            yaxis_title='Region',
            yaxis={'categoryorder':'total ascending'},
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
    
    # Create a bubble chart of property value vs monthly rent if available
    if 'Property Value' in df.columns and 'Monthly Rent' in df.columns:
        fig = px.scatter(
            df,
            x='Property Value',
            y='Monthly Rent',
            size='PTR Ratio' if 'PTR Ratio' in df.columns else None,
            color='Region',
            hover_name='Region',
            title='Property Value vs Monthly Rent',
            labels={
                'Property Value': 'Property Value ($)',
                'Monthly Rent': 'Monthly Rent ($)'
            },
            height=400
        )
        
        # Update layout
        fig.update_layout(
            margin=dict(l=0, r=0, t=40, b=0)
        )
        
        # Display the chart
        st.plotly_chart(fig, use_container_width=True)
