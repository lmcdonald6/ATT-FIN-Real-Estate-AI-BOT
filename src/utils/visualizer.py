"""
Data Visualization Module
Creates interactive charts and visualizations for ATTOM data
"""
from typing import Dict, List, Optional, Union
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json

class DataVisualizer:
    """Creates interactive visualizations for real estate data"""
    
    def __init__(self, theme: str = 'plotly_white'):
        """Initialize with a theme"""
        self.theme = theme
        self.color_palette = px.colors.qualitative.Set3
    
    def create_property_value_chart(self, data: Dict) -> go.Figure:
        """Create an interactive property value chart"""
        historical = data.get('historical_values', [])
        dates = [item['date'] for item in historical]
        values = [item['value'] for item in historical]
        
        fig = go.Figure()
        
        # Historical values line
        fig.add_trace(go.Scatter(
            x=dates,
            y=values,
            name='Historical Value',
            line=dict(color=self.color_palette[0], width=2),
            hovertemplate='Date: %{x}<br>Value: $%{y:,.2f}<extra></extra>'
        ))
        
        # Current value marker
        current_value = data.get('estimated_value', 0)
        fig.add_trace(go.Scatter(
            x=[dates[-1]],
            y=[current_value],
            name='Current Estimate',
            mode='markers',
            marker=dict(size=12, color=self.color_palette[1]),
            hovertemplate='Current Value: $%{y:,.2f}<extra></extra>'
        ))
        
        # Value range
        range_low = data.get('value_range', {}).get('low', current_value * 0.9)
        range_high = data.get('value_range', {}).get('high', current_value * 1.1)
        
        fig.add_trace(go.Scatter(
            x=[dates[-1], dates[-1]],
            y=[range_low, range_high],
            name='Value Range',
            mode='lines',
            line=dict(color=self.color_palette[2], width=2),
            hovertemplate='Range: $%{y:,.2f}<extra></extra>'
        ))
        
        fig.update_layout(
            title='Property Value History and Forecast',
            xaxis_title='Date',
            yaxis_title='Value ($)',
            template=self.theme,
            hovermode='x unified'
        )
        
        return fig
    
    def create_market_trends_chart(self, data: Dict) -> go.Figure:
        """Create an interactive market trends chart"""
        trends = data.get('price_trends', {})
        historical = trends.get('historical_trends', [])
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Median Price Trend',
                'Price per Sqft',
                'Days on Market',
                'Inventory Levels'
            )
        )
        
        # Median Price Trend
        fig.add_trace(
            go.Scatter(
                x=[item['date'] for item in historical],
                y=[item['median_price'] for item in historical],
                name='Median Price',
                line=dict(color=self.color_palette[0])
            ),
            row=1, col=1
        )
        
        # Price per Sqft
        fig.add_trace(
            go.Scatter(
                x=[item['date'] for item in historical],
                y=[item['price_per_sqft'] for item in historical],
                name='Price/Sqft',
                line=dict(color=self.color_palette[1])
            ),
            row=1, col=2
        )
        
        # Days on Market
        fig.add_trace(
            go.Scatter(
                x=[item['date'] for item in historical],
                y=[item['days_on_market'] for item in historical],
                name='Days on Market',
                line=dict(color=self.color_palette[2])
            ),
            row=2, col=1
        )
        
        # Inventory
        fig.add_trace(
            go.Bar(
                x=[item['date'] for item in historical],
                y=[item['inventory'] for item in historical],
                name='Inventory',
                marker_color=self.color_palette[3]
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text='Market Trends Analysis',
            showlegend=True,
            template=self.theme
        )
        
        return fig
    
    def create_demographic_chart(self, data: Dict) -> go.Figure:
        """Create an interactive demographic analysis chart"""
        demo = data.get('demographics', {})
        
        fig = make_subplots(
            rows=2, cols=2,
            specs=[[{'type': 'pie'}, {'type': 'bar'}],
                  [{'type': 'bar'}, {'type': 'scatter'}]],
            subplot_titles=(
                'Household Composition',
                'Income Distribution',
                'Education Levels',
                'Population Growth'
            )
        )
        
        # Household Composition
        households = demo.get('households', {})
        fig.add_trace(
            go.Pie(
                labels=['Owner Occupied', 'Renter Occupied'],
                values=[
                    households.get('owner_occupied', 0),
                    households.get('renter_occupied', 0)
                ],
                marker_colors=[self.color_palette[0], self.color_palette[1]]
            ),
            row=1, col=1
        )
        
        # Income Distribution
        income_dist = demo.get('income', {}).get('income_distribution', {})
        fig.add_trace(
            go.Bar(
                x=list(income_dist.keys()),
                y=list(income_dist.values()),
                marker_color=self.color_palette[2]
            ),
            row=1, col=2
        )
        
        # Education Levels
        education = demo.get('education', {})
        fig.add_trace(
            go.Bar(
                x=['High School', 'Bachelor', 'Graduate'],
                y=[
                    education.get('high_school', 0),
                    education.get('bachelor', 0),
                    education.get('graduate', 0)
                ],
                marker_color=self.color_palette[3]
            ),
            row=2, col=1
        )
        
        # Population Growth
        population = demo.get('population', {})
        growth_data = population.get('growth_trend', [])
        fig.add_trace(
            go.Scatter(
                x=[item['year'] for item in growth_data],
                y=[item['population'] for item in growth_data],
                line=dict(color=self.color_palette[4])
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text='Demographic Analysis',
            showlegend=True,
            template=self.theme
        )
        
        return fig
    
    def create_risk_assessment_chart(self, data: Dict) -> go.Figure:
        """Create an interactive risk assessment chart"""
        risk = data.get('risk', {})
        
        # Create radar chart for risk levels
        natural_hazards = risk.get('natural_hazards', {})
        
        fig = go.Figure()
        
        # Risk Levels Radar
        fig.add_trace(go.Scatterpolar(
            r=[
                natural_hazards.get('flood', {}).get('risk_level', 0),
                natural_hazards.get('earthquake', {}).get('risk_level', 0),
                natural_hazards.get('wildfire', {}).get('risk_level', 0),
                natural_hazards.get('tornado', {}).get('risk_level', 0),
                natural_hazards.get('hurricane', {}).get('risk_level', 0)
            ],
            theta=['Flood', 'Earthquake', 'Wildfire', 'Tornado', 'Hurricane'],
            fill='toself',
            name='Natural Hazards',
            line_color=self.color_palette[0]
        ))
        
        # Environmental Risks
        environmental = risk.get('environmental', {})
        fig.add_trace(go.Scatterpolar(
            r=[
                environmental.get('air_quality', 0),
                environmental.get('water_quality', 0),
                environmental.get('soil_contamination', 0),
                len(environmental.get('toxic_sites', [])),
                risk.get('insurance_factors', {}).get('risk_score', 0)
            ],
            theta=['Air Quality', 'Water Quality', 'Soil Quality', 'Toxic Sites', 'Insurance Risk'],
            fill='toself',
            name='Environmental',
            line_color=self.color_palette[1]
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            title='Risk Assessment Analysis',
            template=self.theme
        )
        
        return fig
    
    def create_school_quality_chart(self, data: Dict) -> go.Figure:
        """Create an interactive school quality visualization"""
        schools = data.get('schools', {})
        assigned = schools.get('assigned_schools', {})
        
        fig = go.Figure()
        
        # Test Scores by School
        for school_type, school_data in assigned.items():
            scores = school_data.get('test_scores', {})
            fig.add_trace(go.Bar(
                name=school_type.title(),
                x=['Math', 'Reading', 'Science'],
                y=[
                    scores.get('math', 0),
                    scores.get('reading', 0),
                    scores.get('science', 0)
                ],
                text=[f"{v}%" for v in [
                    scores.get('math', 0),
                    scores.get('reading', 0),
                    scores.get('science', 0)
                ]],
                textposition='auto',
            ))
        
        fig.update_layout(
            barmode='group',
            title='School Performance Metrics',
            xaxis_title='Subject',
            yaxis_title='Score',
            template=self.theme,
            yaxis=dict(range=[0, 100])
        )
        
        return fig
    
    def create_investment_analysis_chart(self, data: Dict) -> go.Figure:
        """Create an interactive investment analysis chart"""
        investment = data.get('investment_metrics', {})
        
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'ROI Components',
                'Cash Flow Projection',
                'Expense Breakdown',
                'Value Appreciation'
            )
        )
        
        # ROI Components
        roi_components = investment.get('roi_components', {})
        fig.add_trace(
            go.Waterfall(
                name='ROI Components',
                orientation='v',
                measure=['relative'] * len(roi_components),
                x=list(roi_components.keys()),
                y=list(roi_components.values()),
                connector={'line': {'color': 'rgb(63, 63, 63)'}},
                decreasing={'marker': {'color': self.color_palette[0]}},
                increasing={'marker': {'color': self.color_palette[1]}},
                totals={'marker': {'color': self.color_palette[2]}}
            ),
            row=1, col=1
        )
        
        # Cash Flow Projection
        cash_flow = investment.get('cash_flow_projection', [])
        fig.add_trace(
            go.Scatter(
                x=[item['month'] for item in cash_flow],
                y=[item['amount'] for item in cash_flow],
                name='Cash Flow',
                line=dict(color=self.color_palette[3])
            ),
            row=1, col=2
        )
        
        # Expense Breakdown
        expenses = investment.get('expense_breakdown', {})
        fig.add_trace(
            go.Pie(
                labels=list(expenses.keys()),
                values=list(expenses.values()),
                name='Expenses'
            ),
            row=2, col=1
        )
        
        # Value Appreciation
        appreciation = investment.get('value_appreciation', [])
        fig.add_trace(
            go.Scatter(
                x=[item['year'] for item in appreciation],
                y=[item['value'] for item in appreciation],
                name='Property Value',
                line=dict(color=self.color_palette[4])
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text='Investment Analysis',
            showlegend=True,
            template=self.theme
        )
        
        return fig
    
    def create_property_comparison_chart(self, properties: List[Dict]) -> go.Figure:
        """Create comparison chart for multiple properties"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Price vs. Market Value',
                'Equity Distribution',
                'Days on Market',
                'Distress Score'
            )
        )
        
        # Extract data
        addresses = []
        prices = []
        values = []
        equity_pcts = []
        dom = []
        distress_scores = []
        
        for prop in properties:
            info = prop.get('property', {})
            analysis = prop.get('analysis', {})
            
            addresses.append(info.get('address', 'N/A'))
            prices.append(analysis.get('current_price', 0))
            values.append(analysis.get('estimated_value', 0))
            equity_pcts.append(analysis.get('equity_percentage', 0))
            dom.append(analysis.get('days_on_market', 0))
            
            # Calculate distress score
            indicators = analysis.get('distress_indicators', {}).get('indicators', [])
            score = len(indicators) * 20  # Simple scoring: each indicator adds 20 points
            distress_scores.append(min(score, 100))
        
        # Price vs. Value Comparison
        fig.add_trace(
            go.Bar(
                x=addresses,
                y=prices,
                name='Current Price',
                marker_color=self.color_palette[0]
            ),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(
                x=addresses,
                y=values,
                name='Estimated Value',
                marker_color=self.color_palette[1]
            ),
            row=1, col=1
        )
        
        # Equity Distribution
        fig.add_trace(
            go.Bar(
                x=addresses,
                y=equity_pcts,
                name='Equity %',
                marker_color=self.color_palette[2]
            ),
            row=1, col=2
        )
        
        # Days on Market
        fig.add_trace(
            go.Bar(
                x=addresses,
                y=dom,
                name='Days on Market',
                marker_color=self.color_palette[3]
            ),
            row=2, col=1
        )
        
        # Distress Score
        fig.add_trace(
            go.Bar(
                x=addresses,
                y=distress_scores,
                name='Distress Score',
                marker_color=self.color_palette[4]
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text='Property Comparison Analysis',
            showlegend=True,
            template=self.theme
        )
        
        return fig
    
    def create_distress_indicators_chart(self, properties: List[Dict]) -> go.Figure:
        """Create detailed distress indicators analysis"""
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Distress Types Distribution',
                'Severity Levels',
                'Time Since Distress',
                'Financial Impact'
            )
        )
        
        # Collect distress data
        all_indicators = []
        severity_levels = []
        time_periods = []
        financial_impacts = []
        
        for prop in properties:
            analysis = prop.get('analysis', {})
            distress = analysis.get('distress_indicators', {})
            
            # Collect indicators
            indicators = distress.get('indicators', [])
            all_indicators.extend(indicators)
            
            # Collect severity
            severity_levels.append(distress.get('severity', 'low'))
            
            # Time analysis
            time_since = distress.get('time_since_first_indicator', 0)
            time_periods.append(time_since)
            
            # Financial impact
            impact = distress.get('estimated_financial_impact', 0)
            financial_impacts.append(impact)
        
        # Distress Types Distribution
        indicator_counts = pd.Series(all_indicators).value_counts()
        fig.add_trace(
            go.Pie(
                labels=indicator_counts.index,
                values=indicator_counts.values,
                name='Distress Types'
            ),
            row=1, col=1
        )
        
        # Severity Levels
        severity_counts = pd.Series(severity_levels).value_counts()
        fig.add_trace(
            go.Bar(
                x=severity_counts.index,
                y=severity_counts.values,
                name='Severity',
                marker_color=self.color_palette[1]
            ),
            row=1, col=2
        )
        
        # Time Since Distress
        fig.add_trace(
            go.Histogram(
                x=time_periods,
                name='Time Distribution',
                marker_color=self.color_palette[2]
            ),
            row=2, col=1
        )
        
        # Financial Impact
        fig.add_trace(
            go.Box(
                y=financial_impacts,
                name='Financial Impact',
                marker_color=self.color_palette[3]
            ),
            row=2, col=2
        )
        
        fig.update_layout(
            height=800,
            title_text='Distress Indicators Analysis',
            showlegend=True,
            template=self.theme
        )
        
        return fig
    
    def save_chart(self, fig: go.Figure, filename: str) -> None:
        """Save chart to file"""
        try:
            fig.write_html(filename)
        except Exception as e:
            print(f"Error saving chart: {str(e)}")
    
    def save_chart_image(self, fig: go.Figure, filename: str) -> None:
        """Save chart as static image"""
        fig.write_image(filename)
