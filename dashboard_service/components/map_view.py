"""Map View Component

This component displays an interactive map of real estate properties and market data.
"""

import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

# Dictionary of US states with their approximate center coordinates
US_STATES_COORDS = {
    "Alabama": {"lat": 32.806671, "lon": -86.791130},
    "Alaska": {"lat": 61.370716, "lon": -152.404419},
    "Arizona": {"lat": 33.729759, "lon": -111.431221},
    "Arkansas": {"lat": 34.969704, "lon": -92.373123},
    "California": {"lat": 36.116203, "lon": -119.681564},
    "Colorado": {"lat": 39.059811, "lon": -105.311104},
    "Connecticut": {"lat": 41.597782, "lon": -72.755371},
    "Delaware": {"lat": 39.318523, "lon": -75.507141},
    "Florida": {"lat": 27.766279, "lon": -81.686783},
    "Georgia": {"lat": 33.040619, "lon": -83.643074},
    "Hawaii": {"lat": 21.094318, "lon": -157.498337},
    "Idaho": {"lat": 44.240459, "lon": -114.478828},
    "Illinois": {"lat": 40.349457, "lon": -88.986137},
    "Indiana": {"lat": 39.849426, "lon": -86.258278},
    "Iowa": {"lat": 42.011539, "lon": -93.210526},
    "Kansas": {"lat": 38.526600, "lon": -96.726486},
    "Kentucky": {"lat": 37.668140, "lon": -84.670067},
    "Louisiana": {"lat": 31.169546, "lon": -91.867805},
    "Maine": {"lat": 44.693947, "lon": -69.381927},
    "Maryland": {"lat": 39.063946, "lon": -76.802101},
    "Massachusetts": {"lat": 42.230171, "lon": -71.530106},
    "Michigan": {"lat": 43.326618, "lon": -84.536095},
    "Minnesota": {"lat": 45.694454, "lon": -93.900192},
    "Mississippi": {"lat": 32.741646, "lon": -89.678696},
    "Missouri": {"lat": 38.456085, "lon": -92.288368},
    "Montana": {"lat": 46.921925, "lon": -110.454353},
    "Nebraska": {"lat": 41.125370, "lon": -98.268082},
    "Nevada": {"lat": 38.313515, "lon": -117.055374},
    "New Hampshire": {"lat": 43.452492, "lon": -71.563896},
    "New Jersey": {"lat": 40.298904, "lon": -74.521011},
    "New Mexico": {"lat": 34.840515, "lon": -106.248482},
    "New York": {"lat": 42.165726, "lon": -74.948051},
    "North Carolina": {"lat": 35.630066, "lon": -79.806419},
    "North Dakota": {"lat": 47.528912, "lon": -99.784012},
    "Ohio": {"lat": 40.388783, "lon": -82.764915},
    "Oklahoma": {"lat": 35.565342, "lon": -96.928917},
    "Oregon": {"lat": 44.572021, "lon": -122.070938},
    "Pennsylvania": {"lat": 40.590752, "lon": -77.209755},
    "Rhode Island": {"lat": 41.680893, "lon": -71.511780},
    "South Carolina": {"lat": 33.856892, "lon": -80.945007},
    "South Dakota": {"lat": 44.299782, "lon": -99.438828},
    "Tennessee": {"lat": 35.747845, "lon": -86.692345},
    "Texas": {"lat": 31.054487, "lon": -97.563461},
    "Utah": {"lat": 40.150032, "lon": -111.862434},
    "Vermont": {"lat": 44.045876, "lon": -72.710686},
    "Virginia": {"lat": 37.769337, "lon": -78.169968},
    "Washington": {"lat": 47.400902, "lon": -121.490494},
    "West Virginia": {"lat": 38.491226, "lon": -80.954453},
    "Wisconsin": {"lat": 44.268543, "lon": -89.616508},
    "Wyoming": {"lat": 42.755966, "lon": -107.302490},
    # Add major cities as well
    "Atlanta": {"lat": 33.749, "lon": -84.388},
    "Boston": {"lat": 42.361, "lon": -71.057},
    "Chicago": {"lat": 41.878, "lon": -87.630},
    "Dallas": {"lat": 32.779, "lon": -96.808},
    "Denver": {"lat": 39.739, "lon": -104.990},
    "Houston": {"lat": 29.760, "lon": -95.370},
    "Los Angeles": {"lat": 34.052, "lon": -118.244},
    "Miami": {"lat": 25.762, "lon": -80.192},
    "New York City": {"lat": 40.714, "lon": -74.006},
    "Philadelphia": {"lat": 39.953, "lon": -75.165},
    "Phoenix": {"lat": 33.448, "lon": -112.074},
    "San Francisco": {"lat": 37.774, "lon": -122.419},
    "Seattle": {"lat": 47.606, "lon": -122.332},
    "Washington DC": {"lat": 38.907, "lon": -77.037}
}

def prepare_map_data(df):
    """Prepare data for map visualization.
    
    Args:
        df: DataFrame containing market analysis data
        
    Returns:
        DataFrame with latitude and longitude added
    """
    # Create a copy of the dataframe
    map_df = df.copy()
    
    # Add latitude and longitude based on region
    map_df['latitude'] = None
    map_df['longitude'] = None
    
    for idx, row in map_df.iterrows():
        region = row['Region']
        if region in US_STATES_COORDS:
            map_df.at[idx, 'latitude'] = US_STATES_COORDS[region]['lat']
            map_df.at[idx, 'longitude'] = US_STATES_COORDS[region]['lon']
    
    # Drop rows without coordinates
    map_df = map_df.dropna(subset=['latitude', 'longitude'])
    
    return map_df

def display_map(df):
    """Display an interactive map of market analysis data.
    
    Args:
        df: DataFrame containing market analysis data
    """
    if 'Region' not in df.columns:
        st.error("Region data is missing. Cannot display map.")
        return
    
    # Prepare data for map
    map_df = prepare_map_data(df)
    
    if map_df.empty:
        st.warning("No location data available for mapping.")
        return
    
    # Create map view
    st.subheader("Market Analysis Map")
    
    # Let user choose between different map types
    map_type = st.radio(
        "Map Type",
        options=["3D Column Map", "Scatter Map"],
        horizontal=True
    )
    
    if map_type == "3D Column Map":
        # Create 3D column map using PyDeck
        display_3d_column_map(map_df)
    else:
        # Create scatter map using Plotly
        display_scatter_map(map_df)

def display_3d_column_map(df):
    """Display a 3D column map using PyDeck.
    
    Args:
        df: DataFrame containing market analysis data with coordinates
    """
    # Use Final Score for column height if available, otherwise use a default value
    if 'Final Score' in df.columns:
        df['elevation'] = df['Final Score'] * 100  # Scale up for visibility
        color_column = 'Final Score'
    elif 'Score' in df.columns:
        df['elevation'] = df['Score'] * 100  # Scale up for visibility
        color_column = 'Score'
    else:
        df['elevation'] = 5000  # Default height
        color_column = None
    
    # Set the initial view state
    view_state = pdk.ViewState(
        latitude=df['latitude'].mean(),
        longitude=df['longitude'].mean(),
        zoom=3.5,
        pitch=45,
    )
    
    # Define the column layer
    if color_column:
        column_layer = pdk.Layer(
            'ColumnLayer',
            data=df,
            get_position=['longitude', 'latitude'],
            get_elevation='elevation',
            elevation_scale=1,
            radius=50000,
            get_fill_color=["interpolate", ["linear"], ["get", color_column], 
                            0, [255, 0, 0, 255],
                            50, [255, 255, 0, 255],
                            100, [0, 255, 0, 255]],
            pickable=True,
            auto_highlight=True,
        )
    else:
        column_layer = pdk.Layer(
            'ColumnLayer',
            data=df,
            get_position=['longitude', 'latitude'],
            get_elevation='elevation',
            elevation_scale=1,
            radius=50000,
            get_fill_color=[0, 116, 217, 200],
            pickable=True,
            auto_highlight=True,
        )
    
    # Create the deck
    deck = pdk.Deck(
        layers=[column_layer],
        initial_view_state=view_state,
        tooltip={
            "text": "{Region}\n"
                   "Score: {Final Score}\n"
                   "Market Phase: {Market Phase}\n"
                   "Risk Level: {Risk Level}"
        }
    )
    
    # Render the deck
    st.pydeck_chart(deck)

def display_scatter_map(df):
    """Display a scatter map using Plotly.
    
    Args:
        df: DataFrame containing market analysis data with coordinates
    """
    # Determine which columns to use for color and size
    color_column = 'Final Score' if 'Final Score' in df.columns else ('Score' if 'Score' in df.columns else None)
    size_column = 'Property Value' if 'Property Value' in df.columns else ('PropertyValue' if 'PropertyValue' in df.columns else None)
    
    # Create hover text
    df['hover_text'] = df.apply(
        lambda row: f"<b>{row['Region']}</b><br>" +
                   (f"Score: {row['Final Score']:.1f}<br>" if 'Final Score' in df.columns else "") +
                   (f"Market Phase: {row['Market Phase']}<br>" if 'Market Phase' in df.columns else "") +
                   (f"Risk Level: {row['Risk Level']}<br>" if 'Risk Level' in df.columns else "") +
                   (f"Property Value: ${row['Property Value']:,.0f}" if 'Property Value' in df.columns else ""),
        axis=1
    )
    
    # Create the scatter map
    fig = px.scatter_mapbox(
        df,
        lat="latitude",
        lon="longitude",
        hover_name="Region",
        hover_data=["Region"],
        color=color_column if color_column else None,
        size=size_column if size_column else None,
        size_max=15,
        zoom=3,
        height=500,
        color_continuous_scale=px.colors.sequential.Viridis,
        custom_data=['hover_text']
    )
    
    # Update the map layout
    fig.update_layout(
        mapbox_style="carto-positron",
        margin={"r":0,"t":0,"l":0,"b":0},
        mapbox=dict(
            center=dict(
                lat=df['latitude'].mean(),
                lon=df['longitude'].mean()
            ),
            zoom=3.5
        )
    )
    
    # Update hover template
    fig.update_traces(
        hovertemplate="%{customdata[0]}<extra></extra>"
    )
    
    # Display the map
    st.plotly_chart(fig, use_container_width=True)
