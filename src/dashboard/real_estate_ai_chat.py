#!/usr/bin/env python3
"""
Real Estate AI Chat Interface

A Streamlit dashboard that provides a conversational interface to the
Real Estate AI Orchestrator, allowing users to ask natural language questions
about real estate investments, neighborhood sentiment, and market trends.

Features:
- Voice input using Whisper transcription
- Chat history tracking and retrieval
- Export options (PDF, CSV, Excel)
- User profiles and preferences
"""

import os
import sys
import json
import logging
from typing import Dict, Any
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Ensure project directory is in path
sys_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if sys_path not in sys.path:
    sys.path.append(sys_path)

# Import required libraries
try:
    import streamlit as st
    import plotly.express as px
    import pandas as pd
    from dotenv import load_dotenv
    import openai
    from openai import OpenAI
    
    # Load environment variables
    load_dotenv()
    
    # Initialize OpenAI client
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    OPENAI_AVAILABLE = True
except ImportError as e:
    logger.error(f"Required package not installed: {e}")
    OPENAI_AVAILABLE = False

# Import utility modules
try:
    from src.utils.voice_input import transcribe_audio, save_uploaded_audio
    VOICE_INPUT_AVAILABLE = True
except ImportError:
    logger.warning("Voice input module not available.")
    VOICE_INPUT_AVAILABLE = False

try:
    from src.utils.chat_history import log_chat, get_chat_history, load_chat_result, get_full_chat_entry, clear_chat_history
    HISTORY_AVAILABLE = True
except ImportError:
    logger.warning("Chat history module not available.")
    HISTORY_AVAILABLE = False

try:
    from src.utils.export_reports import export_analysis_result
    EXPORT_AVAILABLE = True
except ImportError:
    logger.warning("Export reports module not available.")
    EXPORT_AVAILABLE = False

# Import the orchestrator
try:
    from src.orchestration.real_estate_ai_orchestrator import real_estate_ai_orchestrator
except ImportError:
    logger.error("Could not import real_estate_ai_orchestrator. Make sure it's installed correctly.")
    
    # Mock implementation for testing
    def real_estate_ai_orchestrator(prompt: str) -> Dict[str, Any]:
        """Mock implementation of the orchestrator."""
        return {
            "type": "mock_response",
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": prompt,
            "message": "This is a mock response. The real orchestrator is not available."
        }


def generate_summary(response: Dict[str, Any]) -> str:
    """
    Generate a natural language summary of the analysis results.
    
    Args:
        response: The response from the orchestrator
        
    Returns:
        A natural language summary of the results
    """
    if not OPENAI_AVAILABLE:
        return "OpenAI is not available for generating summaries. Please check the raw results below."
    
    try:
        # Create a prompt based on the response type
        response_type = response.get("type", "unknown")
        
        if response_type == "investment_analysis":
            profile = response.get("investment_profile", {})
            prompt = f"""
            Summarize this real estate investment analysis in a helpful paragraph for a potential investor:
            
            ZIP Code: {response.get('zip')}
            Metro Area: {response.get('metro', 'Unknown')}
            Confidence Score: {profile.get('confidence_score', 0)}/100
            Rating: {profile.get('rating', 'N/A')}
            Recommendation: {profile.get('recommendation', 'N/A')}
            Market Score: {response.get('market_score', 0)}
            Reputation Score: {response.get('reputation_score', 0)}
            Trend Score: {response.get('trend_score', 0)}
            Economic Score: {response.get('econ_score', 0)}
            
            Include the confidence score, rating, and recommendation in your summary.
            Explain what these scores mean for an investor in simple terms.
            """
        
        elif response_type == "zip_comparison":
            results = response.get("results", {})
            zips_info = "\n".join([f"ZIP {z}: Market={data.get('market_score', 0)}, Reputation={data.get('reputation_score', 0)}, Trend={data.get('trend_score', 0)}" 
                                for z, data in results.items()])
            prompt = f"""
            Summarize this comparison of ZIP codes in a helpful paragraph for someone deciding where to invest:
            
            {zips_info}
            
            Compare the ZIP codes and suggest which one might be better for investment based on these scores.
            Explain your reasoning in simple terms.
            """
        
        elif response_type == "street_analysis" or response_type == "multi_street_analysis":
            if response_type == "street_analysis":
                street_info = f"Street: {response.get('street')} in ZIP {response.get('zip')}\nScore: {response.get('score', 0) * 100:.1f}/100\nSummary: {response.get('summary', 'N/A')}"
            else:
                streets = response.get("streets", {})
                street_info = "\n".join([f"Street: {s}\nScore: {response['streets'][s].get('score', 0) * 100:.1f}/100" for s in streets])
                street_info += f"\nAverage Score: {response.get('average_score', 0) * 100:.1f}/100"
            
            prompt = f"""
            Summarize this street-level sentiment analysis in a helpful paragraph for someone interested in the neighborhood:
            
            {street_info}
            
            Explain what these sentiment scores mean for someone considering living or investing in this area.
            Use simple, conversational language.
            """
        
        elif response_type == "metro_investment_comparison":
            ranked = response.get("ranked_metros", [])
            metro_info = "\n".join([f"{i+1}. {metro.upper()}: {score:.1f}/100" for i, (metro, score) in enumerate(ranked)])
            
            prompt = f"""
            Summarize this comparison of metropolitan areas in a helpful paragraph for an investor:
            
            Metro Rankings by Investment Confidence:
            {metro_info}
            
            Explain what these rankings mean and which metro areas might be better for investment.
            Use simple, conversational language.
            """
        
        else:
            # Generic prompt for other response types
            prompt = f"Summarize this real estate analysis result in a helpful paragraph:\n\n{json.dumps(response, indent=2)}"
        
        # Generate summary using OpenAI
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",  # Using 3.5 as fallback since 4-turbo might not be available
            messages=[
                {"role": "system", "content": "You are a helpful real estate investment advisor. Summarize analysis results in clear, concise language that a non-expert can understand."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=250
        )
        
        return completion.choices[0].message.content
    
    except Exception as e:
        logger.error(f"Error generating summary: {e}")
        return f"Could not generate summary: {str(e)}. Please check the raw results below."


def display_investment_analysis(response: Dict[str, Any]):
    """
    Display investment analysis results in a user-friendly format.
    
    Args:
        response: The response from the orchestrator
    """
    profile = response.get("investment_profile", {})
    
    # Create columns for key metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Confidence Score", f"{profile.get('confidence_score', 0)}/100")
    
    with col2:
        rating = profile.get("rating", "N/A")
        # Add color based on rating
        if rating.startswith("A"):
            st.metric("Rating", rating, delta="Good", delta_color="normal")
        elif rating.startswith("B"):
            st.metric("Rating", rating, delta="Moderate", delta_color="normal")
        elif rating.startswith("C"):
            st.metric("Rating", rating, delta="Neutral", delta_color="off")
        else:
            st.metric("Rating", rating, delta="Poor", delta_color="inverse")
    
    with col3:
        st.metric("Recommendation", profile.get("recommendation", "N/A"))
    
    # Create a radar chart of scores
    scores = {
        "Category": ["Market", "Reputation", "Trend", "Economic"],
        "Score": [
            response.get("market_score", 0),
            response.get("reputation_score", 0),
            response.get("trend_score", 0),
            response.get("econ_score", 0)
        ]
    }
    
    df = pd.DataFrame(scores)
    fig = px.line_polar(df, r="Score", theta="Category", line_close=True,
                       range_r=[0, 100], title=f"Investment Profile for {response.get('zip')}")
    st.plotly_chart(fig, use_container_width=True)
    
    # Display metro-specific adjustments if available
    adjustments = response.get("metro_adjustments", {})
    if adjustments:
        st.subheader(f"Metro-Specific Adjustments for {response.get('metro', '').upper()}")
        adj_df = pd.DataFrame({
            "Adjustment": ["Vacancy Penalty", "Crime Penalty", "Permit Bonus"],
            "Value": [
                adjustments.get("vacancy_penalty", 0),
                adjustments.get("crime_penalty", 0),
                adjustments.get("permit_bonus", 0)
            ]
        })
        st.dataframe(adj_df, use_container_width=True)


def display_zip_comparison(response: Dict[str, Any]):
    """
    Display ZIP code comparison results in a user-friendly format.
    
    Args:
        response: The response from the orchestrator
    """
    results = response.get("results", {})
    
    # Create a DataFrame for comparison
    data = []
    for zip_code, zip_data in results.items():
        data.append({
            "ZIP": zip_code,
            "Metro": zip_data.get("metro", "Unknown"),
            "Market Score": zip_data.get("market_score", 0),
            "Reputation Score": zip_data.get("reputation_score", 0),
            "Trend Score": zip_data.get("trend_score", 0),
            "Econ Score": zip_data.get("econ_score", 0)
        })
    
    df = pd.DataFrame(data)
    
    # Create bar chart comparison
    fig = px.bar(df, x="ZIP", y=["Market Score", "Reputation Score", "Trend Score", "Econ Score"],
                barmode="group", title="ZIP Code Comparison")
    st.plotly_chart(fig, use_container_width=True)
    
    # Display data table
    st.dataframe(df, use_container_width=True)


def display_street_analysis(response: Dict[str, Any]):
    """
    Display street-level sentiment analysis results in a user-friendly format.
    
    Args:
        response: The response from the orchestrator
    """
    if response.get("type") == "street_analysis":
        # Single street analysis
        st.subheader(f"Sentiment Analysis: {response.get('street')} ({response.get('zip')})")
        
        # Display score and summary
        col1, col2 = st.columns(2)
        with col1:
            score = response.get("score", 0) * 100
            st.metric("Sentiment Score", f"{score:.1f}/100")
        
        with col2:
            st.metric("Data Source", response.get("platform", "Unknown"))
        
        st.markdown("### Summary")
        st.markdown(response.get("summary", "No summary available"))
        
        # Display sample posts
        st.markdown("### Sample Posts")
        posts = response.get("posts", [])
        
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
    
    else:
        # Multi-street analysis
        st.subheader(f"Multi-Street Analysis for ZIP {response.get('zip')}")
        
        # Display average score
        st.metric("Average Sentiment Score", f"{response.get('average_score', 0) * 100:.1f}/100")
        
        # Create a DataFrame for comparison
        streets_data = response.get("streets", {})
        data = []
        
        for street, street_data in streets_data.items():
            data.append({
                "Street": street,
                "Score": street_data.get("score", 0) * 100,
                "Platform": street_data.get("platform", "Unknown"),
                "Status": street_data.get("status", "Unknown")
            })
        
        df = pd.DataFrame(data)
        
        # Create bar chart comparison
        fig = px.bar(df, x="Street", y="Score", color="Platform",
                    title="Street Sentiment Comparison", labels={"Score": "Sentiment Score (0-100)"})
        st.plotly_chart(fig, use_container_width=True)
        
        # Display data table
        st.dataframe(df, use_container_width=True)


def display_metro_investment_comparison(response: Dict[str, Any]):
    """
    Display metro investment comparison results in a user-friendly format.
    
    Args:
        response: The response from the orchestrator
    """
    # Display metro rankings
    st.subheader("Metro Rankings by Investment Confidence")
    
    ranked_metros = response.get("ranked_metros", [])
    metro_averages = response.get("metro_averages", {})
    
    if ranked_metros:
        # Create a DataFrame for the rankings
        data = []
        for metro, score in ranked_metros:
            avg_data = metro_averages.get(metro, {})
            data.append({
                "Metro": metro.upper(),
                "Confidence Score": score,
                "Market Score": avg_data.get("avg_market_score", 0),
                "Reputation Score": avg_data.get("avg_reputation_score", 0),
                "ZIP Count": avg_data.get("zip_count", 0)
            })
        
        df = pd.DataFrame(data)
        
        # Create bar chart for rankings
        fig = px.bar(df, x="Metro", y="Confidence Score", color="Metro",
                    title="Metro Investment Confidence", labels={"Confidence Score": "Confidence Score (0-100)"})
        st.plotly_chart(fig, use_container_width=True)
        
        # Display data table
        st.dataframe(df, use_container_width=True)
    else:
        st.info("No metro rankings available.")


def main():
    """
    Main function to run the Streamlit dashboard.
    """
    # Page configuration
    st.set_page_config(
        page_title="Real Estate AI Chat",
        page_icon="ud83dudcac",
        layout="wide"
    )
    
    # Initialize session state for user preferences
    if "user_id" not in st.session_state:
        st.session_state.user_id = f"user_{str(uuid.uuid4())[:8]}"
    
    if "favorite_zips" not in st.session_state:
        st.session_state.favorite_zips = []
    
    # Create sidebar for navigation and settings
    with st.sidebar:
        st.title("ud83cudfd9 Real Estate AI")
        
        # Navigation
        page = st.radio("Navigation", ["Chat", "History", "Settings"])
        
        # User profile section
        st.markdown("---")
        st.subheader("ud83dudcbb User Profile")
        st.text(f"ID: {st.session_state.user_id}")
        
        # Favorite ZIP codes
        if st.session_state.favorite_zips:
            st.markdown("**Favorite ZIP Codes:**")
            for zip_code in st.session_state.favorite_zips:
                st.markdown(f"- {zip_code}")
        
        # Clear history button
        if HISTORY_AVAILABLE:
            st.markdown("---")
            if st.button("Clear Chat History"):
                cleared = clear_chat_history(st.session_state.user_id)
                st.success(f"Cleared {cleared} history items")
    
    # Main content area based on selected page
    if page == "Chat":
        display_chat_page()
    elif page == "History":
        display_history_page()
    elif page == "Settings":
        display_settings_page()


def display_chat_page():
    """
    Display the main chat interface.
    """
    # Title and description
    st.title("ud83dudcac Ask the Real Estate Intelligence Bot")
    st.markdown("""
    Ask natural language questions about real estate investments, neighborhood sentiment, and market trends.
    The AI will analyze your query and provide insights based on our comprehensive real estate data.
    """)
    
    # Voice input section
    if VOICE_INPUT_AVAILABLE:
        voice_col1, voice_col2 = st.columns([3, 1])
        
        with voice_col1:
            audio_file = st.file_uploader("Upload audio question", type=["mp3", "wav", "m4a"])
        
        with voice_col2:
            transcribe_button = st.button("ud83cudf99 Transcribe", disabled=audio_file is None)
        
        # Handle audio transcription
        transcription = ""
        if audio_file and transcribe_button:
            with st.spinner("Transcribing audio..."):
                # Save the uploaded file
                audio_path = save_uploaded_audio(audio_file, "temp/audio")
                
                if audio_path:
                    # Transcribe the audio
                    transcription, confidence = transcribe_audio(audio_path)
                    
                    if transcription:
                        st.success(f"Transcribed: {transcription}")
                        
                        # Set as the default text for the input field on next rerun
                        if "chat_input" not in st.session_state:
                            st.session_state["chat_input"] = transcription
                        else:
                            st.session_state["_transcription"] = transcription
                            st.rerun()
                    else:
                        st.error("Failed to transcribe audio. Please try again or type your question.")
    
    # Input area
    # Check if we have a selected example or transcription from a previous run
    default_text = ""
    if "_selected_example" in st.session_state:
        default_text = st.session_state["_selected_example"]
        # Clear it after use
        del st.session_state["_selected_example"]
    elif "_transcription" in st.session_state:
        default_text = st.session_state["_transcription"]
        # Clear it after use
        del st.session_state["_transcription"]
        
    prompt = st.text_input(
        "Type your real estate question:",
        value=default_text,
        placeholder="e.g. Should I invest in 30318 or 11238?",
        key="chat_input"
    )
    
    # Example questions
    st.markdown("### Example Questions")
    example_questions = [
        "What is the investment confidence in 90210 right now?",
        "How does 11238 compare to 30318 in terms of neighborhood buzz and trend?",
        "Tell me about the sentiment on Edgewood Ave in 30318",
        "Compare investment potential between 94110 in SF and 11238 in NYC",
        "What's the market analysis for 60614 in Chicago?"
    ]
    
    # Handle example question selection before rendering input field
    selected_example = None
    cols = st.columns(len(example_questions))
    for i, question in enumerate(example_questions):
        if cols[i].button(f"Example {i+1}", key=f"example_{i}"):
            selected_example = question
            
    # Set default text for the input field
    if selected_example and "chat_input" not in st.session_state:
        st.session_state["chat_input"] = selected_example
    elif selected_example:
        # If we can't set it directly in session state, we'll use rerun
        st.session_state["_selected_example"] = selected_example
        st.rerun()
    
    # Process the query
    analyze_col1, analyze_col2 = st.columns([3, 1])
    
    with analyze_col1:
        analyze_button = st.button("ud83dudcca Analyze", type="primary", disabled=not prompt)
    
    # Process the query
    if analyze_button and prompt:
        st.markdown("---")
        
        with st.spinner("Thinking like an investor and a neighbor..."):
            # Call the orchestrator
            response = real_estate_ai_orchestrator(prompt)
            
            # Log the chat if history is available
            chat_id = None
            if HISTORY_AVAILABLE:
                chat_id = log_chat(prompt, response, st.session_state.user_id)
            
            # Check for errors
            if "error" in response:
                st.error(response["error"])
            else:
                # Generate and display summary
                st.subheader("ud83dudcca AI-Generated Response")
                summary = generate_summary(response)
                st.markdown(summary)
                
                # Export options
                if EXPORT_AVAILABLE:
                    st.markdown("""
                    <div style='display: flex; justify-content: flex-end;'>
                        <p>Export as: </p>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    export_col1, export_col2, export_col3 = st.columns([1, 1, 1])
                    
                    with export_col1:
                        if st.button("ud83dudcdd PDF"):
                            with st.spinner("Generating PDF..."):
                                pdf_path = export_analysis_result(response, "pdf")
                                if pdf_path:
                                    st.success(f"PDF exported to: {pdf_path}")
                                else:
                                    st.error("Failed to generate PDF")
                    
                    with export_col2:
                        if st.button("ud83dudcce CSV"):
                            with st.spinner("Generating CSV..."):
                                csv_path = export_analysis_result(response, "csv")
                                if csv_path:
                                    st.success(f"CSV exported to: {csv_path}")
                                else:
                                    st.error("Failed to generate CSV")
                    
                    with export_col3:
                        if st.button("ud83dudccb Excel"):
                            with st.spinner("Generating Excel..."):
                                excel_path = export_analysis_result(response, "excel")
                                if excel_path:
                                    st.success(f"Excel exported to: {excel_path}")
                                else:
                                    st.error("Failed to generate Excel")
                
                # Save to favorites option
                zip_code = response.get("zip")
                if zip_code and zip_code not in st.session_state.favorite_zips:
                    if st.button(f"ud83dudccd Add ZIP {zip_code} to Favorites"):
                        st.session_state.favorite_zips.append(zip_code)
                        st.success(f"Added ZIP {zip_code} to favorites")
                
                # Display visualizations based on response type
                st.markdown("---")
                st.subheader("ud83dudcc8 Detailed Analysis")
                
                response_type = response.get("type", "unknown")
                
                if response_type == "investment_analysis":
                    display_investment_analysis(response)
                
                elif response_type == "zip_comparison":
                    display_zip_comparison(response)
                
                elif response_type in ["street_analysis", "multi_street_analysis", "street_sentiment"]:
                    display_street_analysis(response)
                
                elif response_type == "metro_investment_comparison":
                    display_metro_investment_comparison(response)
                
                # Display raw JSON in an expander
                with st.expander("View Raw JSON Response"):
                    st.json(response)


def display_history_page():
    """
    Display the chat history page.
    """
    st.title("ud83dudcdc Chat History")
    
    if not HISTORY_AVAILABLE:
        st.warning("Chat history functionality is not available.")
        return
    
    # Get chat history for the current user
    history = get_chat_history(st.session_state.user_id)
    
    if not history:
        st.info("No chat history available. Start asking questions to build your history.")
        return
    
    # Display history items
    for item in history:
        with st.expander(f"{item['timestamp'][:16]} - {item['query']}"):
            # Load the full chat entry
            chat_entry = get_full_chat_entry(item['id'])
            result = chat_entry.get("result", {})
            
            # Display basic info
            st.markdown(f"**Query:** {chat_entry.get('query', 'N/A')}")
            st.markdown(f"**Type:** {result.get('type', 'N/A')}")
            
            # Display specific info based on result type
            result_type = result.get("type", "unknown")
            
            if result_type == "investment_analysis":
                profile = result.get("investment_profile", {})
                st.markdown(f"**ZIP:** {result.get('zip', 'N/A')}")
                st.markdown(f"**Metro:** {result.get('metro', 'N/A')}")
                st.markdown(f"**Confidence Score:** {profile.get('confidence_score', 'N/A')}")
                st.markdown(f"**Rating:** {profile.get('rating', 'N/A')}")
                st.markdown(f"**Recommendation:** {profile.get('recommendation', 'N/A')}")
            
            elif result_type == "zip_comparison":
                zips = result.get("zips", [])
                st.markdown(f"**Compared ZIPs:** {', '.join(zips)}")
            
            # Rerun button
            if st.button("Rerun Analysis", key=f"rerun_{item['id']}"):
                st.session_state["chat_input"] = chat_entry.get('query', '')
                st.session_state["_page"] = "Chat"
                st.rerun()
            
            # Export options
            if EXPORT_AVAILABLE:
                export_col1, export_col2, export_col3 = st.columns([1, 1, 1])
                
                with export_col1:
                    if st.button("Export as PDF", key=f"pdf_{item['id']}"):
                        with st.spinner("Generating PDF..."):
                            pdf_path = export_analysis_result(result, "pdf")
                            if pdf_path:
                                st.success(f"PDF exported to: {pdf_path}")
                            else:
                                st.error("Failed to generate PDF")


def display_settings_page():
    """
    Display the settings page.
    """
    st.title("ud83dudd27 Settings")
    
    # User ID settings
    st.subheader("User Profile")
    st.text(f"Current User ID: {st.session_state.user_id}")
    
    if st.button("Generate New User ID"):
        st.session_state.user_id = f"user_{str(uuid.uuid4())[:8]}"
        st.success(f"New User ID generated: {st.session_state.user_id}")
        st.rerun()
    
    # Favorite ZIP codes
    st.subheader("Favorite ZIP Codes")
    
    if st.session_state.favorite_zips:
        for i, zip_code in enumerate(st.session_state.favorite_zips):
            col1, col2 = st.columns([3, 1])
            
            with col1:
                st.text(zip_code)
            
            with col2:
                if st.button("Remove", key=f"remove_zip_{i}"):
                    st.session_state.favorite_zips.remove(zip_code)
                    st.success(f"Removed ZIP {zip_code} from favorites")
                    st.rerun()
    else:
        st.info("No favorite ZIP codes. Add some by analyzing ZIP codes and clicking 'Add to Favorites'.")
    
    # Add new favorite ZIP
    new_zip = st.text_input("Add ZIP Code", key="new_zip")
    if st.button("Add") and new_zip:
        if new_zip in st.session_state.favorite_zips:
            st.warning(f"ZIP {new_zip} is already in favorites")
        else:
            st.session_state.favorite_zips.append(new_zip)
            st.success(f"Added ZIP {new_zip} to favorites")
            st.rerun()
    
    # Export settings
    if EXPORT_AVAILABLE:
        st.subheader("Export Settings")
        st.text("Default export location: output/")
    
    # Voice input settings
    if VOICE_INPUT_AVAILABLE:
        st.subheader("Voice Input Settings")
        use_whisper = st.checkbox("Use OpenAI Whisper for transcription", value=True)
        st.session_state["use_whisper"] = use_whisper


if __name__ == "__main__":
    main()
