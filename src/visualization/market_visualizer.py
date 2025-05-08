"""Visualization tools for market analysis and opportunity detection."""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import Dict, List, Optional
import json

class MarketVisualizer:
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or {}
        self.color_scheme = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e',
            'success': '#2ca02c',
            'warning': '#d62728',
            'neutral': '#7f7f7f'
        }
        
    def create_opportunity_dashboard(self,
                                   opportunities: List[Dict],
                                   market_data: pd.DataFrame) -> Dict[str, go.Figure]:
        """Create interactive dashboard for investment opportunities."""
        dashboard = {
            'opportunity_map': self.plot_opportunity_map(opportunities),
            'value_analysis': self.plot_value_analysis(opportunities),
            'market_trends': self.plot_market_trends(market_data),
            'opportunity_scores': self.plot_opportunity_scores(opportunities)
        }
        
        return dashboard
    
    def plot_opportunity_map(self, opportunities: List[Dict]) -> go.Figure:
        """Create interactive map of investment opportunities."""
        df = pd.DataFrame(opportunities)
        
        fig = go.Figure()
        
        # Add scatter mapbox for properties
        fig.add_trace(go.Scattermapbox(
            lat=df['latitude'],
            lon=df['longitude'],
            mode='markers',
            marker=go.scattermapbox.Marker(
                size=10,
                color=df['opportunity_score'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Opportunity Score')
            ),
            text=df.apply(
                lambda x: f"Address: {x['address']}<br>"
                         f"Price: ${x['price']:,.0f}<br>"
                         f"Potential Value: ${x['potential_value']:,.0f}<br>"
                         f"Score: {x['opportunity_score']:.1f}",
                axis=1
            ),
            hoverinfo='text'
        ))
        
        # Update layout
        fig.update_layout(
            mapbox=dict(
                style='carto-positron',
                zoom=10,
                center=dict(
                    lat=df['latitude'].mean(),
                    lon=df['longitude'].mean()
                )
            ),
            margin=dict(l=0, r=0, t=30, b=0),
            title='Investment Opportunities Map'
        )
        
        return fig
    
    def plot_value_analysis(self, opportunities: List[Dict]) -> go.Figure:
        """Create value analysis visualization."""
        df = pd.DataFrame(opportunities)
        
        fig = go.Figure()
        
        # Add scatter plot
        fig.add_trace(go.Scatter(
            x=df['price'],
            y=df['potential_value'],
            mode='markers',
            marker=dict(
                size=10,
                color=df['opportunity_score'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Opportunity Score')
            ),
            text=df.apply(
                lambda x: f"Address: {x['address']}<br>"
                         f"Upside: {x['upside_percentage']:.1f}%",
                axis=1
            ),
            hoverinfo='text'
        ))
        
        # Add reference line
        max_value = max(df['price'].max(), df['potential_value'].max())
        fig.add_trace(go.Scatter(
            x=[0, max_value],
            y=[0, max_value],
            mode='lines',
            line=dict(dash='dash', color='gray'),
            name='Fair Value'
        ))
        
        # Update layout
        fig.update_layout(
            title='Property Value Analysis',
            xaxis_title='Current Price ($)',
            yaxis_title='Potential Value ($)',
            showlegend=False
        )
        
        return fig
    
    def plot_market_trends(self, market_data: pd.DataFrame) -> go.Figure:
        """Create market trends visualization."""
        fig = go.Figure()
        
        # Add price trend
        fig.add_trace(go.Scatter(
            x=market_data['period'],
            y=market_data['median_price'],
            name='Median Price',
            line=dict(color=self.color_scheme['primary'])
        ))
        
        # Add volume
        fig.add_trace(go.Bar(
            x=market_data['period'],
            y=market_data['active_listings'],
            name='Active Listings',
            yaxis='y2',
            marker_color=self.color_scheme['secondary'],
            opacity=0.3
        ))
        
        # Update layout
        fig.update_layout(
            title='Market Trends Analysis',
            xaxis_title='Date',
            yaxis_title='Median Price ($)',
            yaxis2=dict(
                title='Active Listings',
                overlaying='y',
                side='right'
            ),
            showlegend=True
        )
        
        return fig
    
    def plot_opportunity_scores(self, opportunities: List[Dict]) -> go.Figure:
        """Create opportunity score breakdown visualization."""
        df = pd.DataFrame(opportunities)
        
        # Sort by opportunity score
        df = df.sort_values('opportunity_score', ascending=True)
        
        fig = go.Figure()
        
        # Add horizontal bar chart
        fig.add_trace(go.Bar(
            y=df['address'],
            x=df['opportunity_score'],
            orientation='h',
            marker_color=df['opportunity_score'],
            colorscale='Viridis',
            text=df['opportunity_score'].round(1),
            textposition='auto',
        ))
        
        # Update layout
        fig.update_layout(
            title='Investment Opportunity Scores',
            xaxis_title='Opportunity Score',
            yaxis_title='Property',
            showlegend=False,
            height=max(400, len(opportunities) * 30)  # Dynamic height
        )
        
        return fig
    
    def create_market_health_dashboard(self, market_data: pd.DataFrame) -> Dict[str, go.Figure]:
        """Create market health monitoring dashboard."""
        dashboard = {
            'price_trends': self.plot_price_trends(market_data),
            'inventory_analysis': self.plot_inventory_analysis(market_data),
            'market_efficiency': self.plot_market_efficiency(market_data),
            'sales_velocity': self.plot_sales_velocity(market_data)
        }
        
        return dashboard
    
    def plot_price_trends(self, market_data: pd.DataFrame) -> go.Figure:
        """Create price trends visualization with moving averages."""
        fig = go.Figure()
        
        # Calculate moving averages
        market_data['MA_3'] = market_data['median_price'].rolling(window=3).mean()
        market_data['MA_6'] = market_data['median_price'].rolling(window=6).mean()
        
        # Add price line
        fig.add_trace(go.Scatter(
            x=market_data['period'],
            y=market_data['median_price'],
            name='Median Price',
            line=dict(color=self.color_scheme['primary'])
        ))
        
        # Add moving averages
        fig.add_trace(go.Scatter(
            x=market_data['period'],
            y=market_data['MA_3'],
            name='3-Month MA',
            line=dict(dash='dash')
        ))
        
        fig.add_trace(go.Scatter(
            x=market_data['period'],
            y=market_data['MA_6'],
            name='6-Month MA',
            line=dict(dash='dot')
        ))
        
        # Update layout
        fig.update_layout(
            title='Price Trends Analysis',
            xaxis_title='Date',
            yaxis_title='Price ($)',
            showlegend=True
        )
        
        return fig
    
    def plot_inventory_analysis(self, market_data: pd.DataFrame) -> go.Figure:
        """Create inventory analysis visualization."""
        fig = go.Figure()
        
        # Add active listings
        fig.add_trace(go.Bar(
            x=market_data['period'],
            y=market_data['active_listings'],
            name='Active Listings',
            marker_color=self.color_scheme['primary']
        ))
        
        # Add sold listings
        fig.add_trace(go.Bar(
            x=market_data['period'],
            y=market_data['sold_listings'],
            name='Sold Listings',
            marker_color=self.color_scheme['success']
        ))
        
        # Calculate months of inventory
        months_inventory = (
            market_data['active_listings'] /
            market_data['sold_listings'].rolling(window=3).mean()
        )
        
        # Add months of inventory line
        fig.add_trace(go.Scatter(
            x=market_data['period'],
            y=months_inventory,
            name='Months of Inventory',
            yaxis='y2',
            line=dict(color=self.color_scheme['secondary'])
        ))
        
        # Update layout
        fig.update_layout(
            title='Inventory Analysis',
            xaxis_title='Date',
            yaxis_title='Number of Listings',
            yaxis2=dict(
                title='Months of Inventory',
                overlaying='y',
                side='right'
            ),
            barmode='group',
            showlegend=True
        )
        
        return fig
    
    def plot_market_efficiency(self, market_data: pd.DataFrame) -> go.Figure:
        """Create market efficiency visualization."""
        fig = go.Figure()
        
        # Calculate efficiency metrics
        market_data['price_to_list_ratio'] = (
            market_data['sold_price'] / market_data['list_price']
        )
        market_data['dom_ma'] = market_data['avg_days_on_market'].rolling(window=3).mean()
        
        # Add price to list ratio
        fig.add_trace(go.Scatter(
            x=market_data['period'],
            y=market_data['price_to_list_ratio'],
            name='Price/List Ratio',
            line=dict(color=self.color_scheme['primary'])
        ))
        
        # Add days on market
        fig.add_trace(go.Scatter(
            x=market_data['period'],
            y=market_data['dom_ma'],
            name='Days on Market (3M MA)',
            yaxis='y2',
            line=dict(color=self.color_scheme['secondary'])
        ))
        
        # Update layout
        fig.update_layout(
            title='Market Efficiency Metrics',
            xaxis_title='Date',
            yaxis_title='Price/List Ratio',
            yaxis2=dict(
                title='Days on Market',
                overlaying='y',
                side='right'
            ),
            showlegend=True
        )
        
        return fig
    
    def plot_sales_velocity(self, market_data: pd.DataFrame) -> go.Figure:
        """Create sales velocity visualization."""
        fig = go.Figure()
        
        # Calculate sales velocity metrics
        market_data['sales_rate'] = (
            market_data['sold_listings'] /
            (market_data['active_listings'] + market_data['sold_listings'])
        )
        market_data['sales_rate_ma'] = market_data['sales_rate'].rolling(window=3).mean()
        
        # Add sales rate
        fig.add_trace(go.Scatter(
            x=market_data['period'],
            y=market_data['sales_rate_ma'],
            name='Sales Rate (3M MA)',
            line=dict(color=self.color_scheme['primary'])
        ))
        
        # Add reference lines
        fig.add_hline(
            y=0.5,
            line_dash='dash',
            line_color='gray',
            annotation_text='Balanced Market'
        )
        
        # Update layout
        fig.update_layout(
            title='Sales Velocity Analysis',
            xaxis_title='Date',
            yaxis_title='Sales Rate',
            yaxis_range=[0, 1],
            showlegend=True
        )
        
        return fig
    
    def export_dashboard(self,
                        dashboard: Dict[str, go.Figure],
                        output_dir: str) -> None:
        """Export dashboard visualizations to HTML files."""
        for name, fig in dashboard.items():
            output_path = f"{output_dir}/{name}.html"
            fig.write_html(output_path)
            
    def to_json(self,
                dashboard: Dict[str, go.Figure],
                output_path: str) -> None:
        """Export dashboard data to JSON for web integration."""
        dashboard_data = {}
        
        for name, fig in dashboard.items():
            dashboard_data[name] = fig.to_json()
            
        with open(output_path, 'w') as f:
            json.dump(dashboard_data, f)
