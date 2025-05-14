#!/usr/bin/env python3
"""
Real Estate AI Chat Runner

This script provides a convenient way to launch the Real Estate AI Chat dashboard.
"""

import os
import sys
import subprocess

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Check for required packages
try:
    import streamlit
    import plotly.express as px
    import pandas as pd
    from dotenv import load_dotenv
    import openai
    from openai import OpenAI
except ImportError as e:
    print(f"Required package not installed: {e}")
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", os.path.join(sys_path, "requirements.txt")])


def main():
    """
    Launch the Real Estate AI Chat dashboard.
    """
    dashboard_path = os.path.join(sys_path, "src", "dashboard", "real_estate_ai_chat.py")
    
    if not os.path.exists(dashboard_path):
        print(f"Error: Dashboard file not found at {dashboard_path}")
        return
    
    print("\nud83dudcac Launching Real Estate AI Chat Dashboard...")
    print("\nThis will open a new browser window with the dashboard.")
    print("Press Ctrl+C in this terminal to stop the dashboard.")
    
    # Launch the dashboard
    subprocess.run([sys.executable, "-m", "streamlit", "run", dashboard_path])


if __name__ == "__main__":
    main()
