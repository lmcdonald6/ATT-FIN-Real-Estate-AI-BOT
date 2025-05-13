"""Real Estate Market Analysis Web Interface

A Streamlit-based web interface for the real estate market analysis tool
with chat and classic input modes, enhanced with GPT-4 for natural language processing.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import re
import os
from typing import Tuple, Optional, Dict, Any
from openai import OpenAI

from modules.analyze_market import analyze_market
from modules.market_export_formatter import format_market_export

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Page configuration
st.set_page_config(
    page_title="🧠 Real Estate AI Concierge",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-row {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
    }
    .risk-high { color: #ff4b4b; }
    .risk-moderate { color: #ffa500; }
    .risk-low { color: #00cc00; }
    </style>
""", unsafe_allow_html=True)

def parse_prompt(prompt):
    """Parse natural language input using GPT-4 for market analysis parameters"""
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                    "role": "user",
                    "content": f"""
Extract the following fields from this real estate inquiry:
- region (city or metro)
- property value in dollars
- monthly rent
- annual household income (if provided)

Return as a Python dictionary.

User prompt:
{prompt}
"""
                }
            ],
            max_tokens=200,
            temperature=0.2
        )
        output = response.choices[0].message.content.strip()
        if output.startswith("{") and output.endswith("}"):
            return eval(output, {"__builtins__": {}})
        else:
            return {"error": "Invalid response format from GPT."}
    except Exception as e:
        return {"error": str(e)}

def display_metrics(export_row: dict):
    """Display market analysis metrics in a structured layout"""
    # Core metrics
    st.markdown("### 📊 Core Metrics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Overall Score", f"{export_row['Final Score']:.1f}/100")
    with col2:
        st.metric("Market Phase", export_row['Market Phase'])
    with col3:
        risk_level = export_row['Risk Level']
        risk_color = {
            'High': 'risk-high',
            'Moderate': 'risk-moderate',
            'Low': 'risk-low'
        }.get(risk_level, '')
        st.markdown(f"**Risk Level:** <span class='{risk_color}'>{risk_level}</span>", unsafe_allow_html=True)
    
    # Market indicators
    st.markdown("### 📈 Market Indicators")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Trend Score", f"{export_row['Trend Score']:.1f}")
    with col2:
        st.metric("Economic Score", f"{export_row['Economic Score']:.1f}")
    with col3:
        st.metric("Price-to-Rent", f"{export_row['PTR Ratio']:.2f}")
    with col4:
        st.metric("Cap Rate", f"{export_row['Cap Rate']:.2f}%")
    
    # Market dynamics
    st.markdown("### 🏘️ Market Dynamics")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Monthly Sales", export_row['Monthly Sales'])
    with col2:
        st.metric("Inventory Level", export_row['Inventory Level'])
    with col3:
        st.metric("Appreciation", f"{export_row['Avg Appreciation']:.1f}%")

def main():
    # Header
    st.title("🏰 Welcome to Your Market Butler")
    st.caption("Your personal AI assistant for smart real estate decisions.")
    
    # Sidebar guidance
    with st.sidebar:
        st.header("🔍 Explore Like a Pro")
        st.markdown("**Try asking about:**")
        st.markdown("- Is a $300k house in Chicago a good investment?")
        st.markdown("- Should I buy a property in Atlanta with $2000 monthly rent?")
        st.markdown("- What's the market like in Los Angeles for a $600k property?")
        st.divider()
        st.markdown("Switch to classic search if you prefer control.")
    
    # Mode selection
    mode = st.radio(
        "Choose Input Style:",
        ["💬 Chat with Butler", "🧾 Classic Property Form"],
        horizontal=True
    )
    
    if mode == "💬 Chat with Butler":
        st.subheader("Talk to Your Market Butler")
        user_prompt = st.text_area(
            "Type your question or scenario:",
            placeholder="e.g., I'm thinking about buying a $300k home in Atlanta with $2500 rent"
        )
        
        if st.button("Run Analysis", key="chat_mode"):
            if user_prompt:
                result = parse_prompt(user_prompt)
                
                if "error" in result:
                    st.error(f"❌ {result['error']}")
                    return
                
                region = result.get("region")
                rent = result.get("rent")
                value = result.get("value")
                income = result.get("income", 85000)
                
                if not all([region, rent, value]):
                    st.error("❌ Could not understand all required details. Please include city, property value, and rent.")
                    return
                
                with st.spinner("🔄 Analyzing market data..."):
                    result = analyze_market(region, rent, value, income)
                    if result.error:
                        st.error(f"❌ {result.error}")
                        return
                    
                    export_row = format_market_export(result.__dict__)
                    display_metrics(export_row)
                    
                    # GPT Analysis
                    if result.gpt_summary:
                        st.markdown("### 🧠 AI Investment Insights")
                        st.info(result.gpt_summary)
                    
                    # Export option
                    st.download_button(
                        label="📤 Export Analysis to CSV",
                        data=pd.DataFrame([export_row]).to_csv(index=False),
                        file_name=f"{region.lower().replace(' ','_')}_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                        mime="text/csv"
                    )
            else:
                st.warning("Please enter your question or scenario.")
    
    else:  # Classic Form Mode
        st.subheader("Structured Market Search")
        with st.form("market_form"):
            region = st.text_input("Region (e.g. Atlanta, Chicago, Los Angeles):", "Atlanta")
            rent = st.number_input("Monthly Rent ($)", min_value=500, max_value=10000, value=2400)
            value = st.number_input("Property Value ($)", min_value=50000, max_value=2000000, value=330000)
            income = st.number_input("Annual Household Income ($)", min_value=20000, max_value=500000, value=85000)
            submitted = st.form_submit_button("Run Analysis")
        
        if submitted:
            with st.spinner("🔄 Analyzing market data..."):
                result = analyze_market(region, rent, value, income)
                if result.error:
                    st.error(f"❌ {result.error}")
                    return
                
                export_row = format_market_export(result.__dict__)
                display_metrics(export_row)
                
                # GPT Analysis
                if result.gpt_summary:
                    st.markdown("### 🧠 AI Investment Insights")
                    st.info(result.gpt_summary)
                
                # Export option
                st.download_button(
                    label="📤 Export Analysis to CSV",
                    data=pd.DataFrame([export_row]).to_csv(index=False),
                    file_name=f"{region.lower().replace(' ','_')}_analysis_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()
