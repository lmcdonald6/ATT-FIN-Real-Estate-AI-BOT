"""
Neighborhood Sentiment Analysis Module (v2)

This module provides functionality to analyze neighborhood sentiment using multiple approaches:
1. Web search results for neighborhood reviews
2. Simulated data based on neighborhood characteristics when web scraping fails
3. OpenAI's GPT models to summarize and analyze sentiment
"""

import asyncio
import os
import logging
import json
import random
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple

import openai
from playwright.async_api import async_playwright, Page, Browser, TimeoutError
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    logger.warning("OPENAI_API_KEY not found in environment variables")

# Initialize OpenAI client
client = openai.OpenAI(api_key=openai_api_key)


async def scrape_google_reviews(query: str, max_results: int = 8) -> List[Dict[str, str]]:
    """
    Uses Playwright to search Google for neighborhood reviews and extract snippets.
    
    Args:
        query: The search query for the neighborhood
        max_results: Maximum number of search results to extract
        
    Returns:
        List of dictionaries containing title and snippet from search results
    """
    results = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = await context.new_page()
            
            # Construct search URL for neighborhood reviews
            search_url = f"https://www.google.com/search?q={query.replace(' ', '+')}+neighborhood+reviews+living"
            logger.info(f"Searching Google with URL: {search_url}")
            
            await page.goto(search_url)
            await page.wait_for_load_state("networkidle")
            
            # Extract search results
            search_results = await page.query_selector_all("div.g")
            logger.info(f"Found {len(search_results)} Google search results")
            
            for i, result in enumerate(search_results[:max_results]):
                try:
                    # Extract title
                    title_elem = await result.query_selector("h3")
                    title = await title_elem.inner_text() if title_elem else "No title"
                    
                    # Extract snippet
                    snippet_elem = await result.query_selector("div.VwiC3b")
                    snippet = await snippet_elem.inner_text() if snippet_elem else ""
                    
                    # Extract URL
                    link_elem = await result.query_selector("a")
                    url = await link_elem.get_attribute("href") if link_elem else None
                    
                    if snippet and len(snippet) > 30:
                        results.append({
                            "title": title,
                            "content": snippet,
                            "url": url
                        })
                        
                except Exception as e:
                    logger.error(f"Error extracting search result {i}: {str(e)}")
                    continue
            
            await browser.close()
            
    except Exception as e:
        logger.error(f"Error during Google scraping: {str(e)}")
    
    return results


async def get_neighborhood_characteristics(location: str) -> Dict[str, Any]:
    """
    Uses OpenAI to generate key characteristics of a neighborhood based on its name.
    This is used as a fallback when web scraping fails.
    
    Args:
        location: The neighborhood or location name
        
    Returns:
        Dictionary with neighborhood characteristics
    """
    try:
        prompt = f"""
Generate realistic characteristics for the neighborhood: {location}
Include information about:
1. Location and geography
2. Demographics and population
3. Housing market (prices, types of housing)
4. Amenities (restaurants, parks, shopping)
5. Transportation options
6. Schools and education
7. Safety and crime statistics
8. Community vibe and culture

Format your response as a JSON object with these categories as keys and detailed descriptions as values.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a real estate data specialist with deep knowledge of neighborhoods across the United States."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=800
        )
        
        characteristics = json.loads(response.choices[0].message.content)
        return characteristics
        
    except Exception as e:
        logger.error(f"Error generating neighborhood characteristics: {str(e)}")
        return {
            "location": location,
            "error": str(e)
        }


async def generate_simulated_reviews(location: str, characteristics: Dict[str, Any], count: int = 5) -> List[Dict[str, str]]:
    """
    Generates simulated neighborhood reviews based on characteristics.
    Used as a fallback when web scraping fails.
    
    Args:
        location: The neighborhood name
        characteristics: Dictionary of neighborhood characteristics
        count: Number of simulated reviews to generate
        
    Returns:
        List of dictionaries containing simulated reviews
    """
    try:
        # Convert characteristics to a string format for the prompt
        chars_text = "\n".join([f"{k}: {v}" for k, v in characteristics.items()])
        
        prompt = f"""
Based on these characteristics of {location}:

{chars_text}

Generate {count} realistic and diverse reviews that people might write about living in this neighborhood.
Each review should:
1. Have a different perspective (resident, visitor, new homeowner, long-time resident, etc.)
2. Include specific details about the neighborhood
3. Have a mix of positive and negative points
4. Feel authentic and conversational
5. Vary in length and tone

Format your response as a JSON array of objects, where each object has:
- "title": A title for the review
- "content": The full review text
- "author_type": The type of person writing the review (e.g., "resident", "visitor")
- "rating": A numerical rating from 1-5

Return ONLY the JSON array with no additional text.
"""

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a simulator of realistic neighborhood reviews."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"},
            max_tokens=1500
        )
        
        simulated_reviews = json.loads(response.choices[0].message.content)
        
        # Format the reviews to match our expected structure
        formatted_reviews = []
        for review in simulated_reviews:
            formatted_reviews.append({
                "title": review["title"],
                "content": f"[{review['author_type']} - {review['rating']}/5 stars] {review['content']}",
                "url": None,
                "simulated": True
            })
            
        return formatted_reviews
        
    except Exception as e:
        logger.error(f"Error generating simulated reviews: {str(e)}")
        return []


def summarize_sentiment_with_gpt(posts: List[Dict[str, str]], location: str) -> str:
    """
    Summarizes the sentiment of neighborhood reviews using OpenAI's GPT model.
    
    Args:
        posts: List of dictionaries containing post information
        location: The neighborhood name
        
    Returns:
        Summarized sentiment analysis as a string
    """
    if not posts:
        return "No data available for sentiment analysis."
    
    # Format posts for the prompt
    formatted_posts = "\n\n".join([
        f"REVIEW TITLE: {post['title']}\nCONTENT: {post['content'][:500]}..." 
        for post in posts
    ])
    
    prompt = f"""
Analyze the sentiment of the following reviews about {location} and summarize how people feel about this neighborhood:

{formatted_posts}

Return a summary with:
1. Overall sentiment score (1-10, where 10 is extremely positive)
2. Key themes mentioned (at least 3-5 themes)
3. Specific positive aspects mentioned
4. Specific concerns or negative aspects mentioned
5. Any notable contradictions in opinions
6. Who would likely enjoy living in this neighborhood
7. Who might not enjoy living in this neighborhood
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a real estate market analyst specializing in neighborhood sentiment analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=800
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error during OpenAI API call: {str(e)}")
        return f"Error generating sentiment summary: {str(e)}"


async def analyze_neighborhood_sentiment(location_query: str, max_results: int = 8) -> Dict[str, Any]:
    """
    Main function to analyze neighborhood sentiment using multiple approaches.
    
    Args:
        location_query: The neighborhood or location to analyze
        max_results: Maximum number of reviews to analyze
        
    Returns:
        Dictionary containing sentiment analysis results
    """
    logger.info(f"Analyzing sentiment for location: {location_query}")
    
    # Try to get real reviews from Google search
    posts = await scrape_google_reviews(location_query, max_results)
    
    # If web scraping fails, use simulated data based on neighborhood characteristics
    if not posts:
        logger.info(f"No web reviews found for {location_query}, generating simulated data")
        characteristics = await get_neighborhood_characteristics(location_query)
        posts = await generate_simulated_reviews(location_query, characteristics)
        data_source = "simulated"
    else:
        data_source = "web_search"
    
    if not posts:
        return {
            "location": location_query,
            "success": False,
            "message": f"Could not generate sentiment data for: {location_query}",
            "data_source": None,
            "posts_analyzed": 0,
            "sentiment_summary": None,
            "timestamp": datetime.now().isoformat()
        }
    
    summary = summarize_sentiment_with_gpt(posts, location_query)
    
    return {
        "location": location_query,
        "success": True,
        "data_source": data_source,
        "posts_analyzed": len(posts),
        "sentiment_summary": summary,
        "sources": [post.get("url") for post in posts if post.get("url")],
        "timestamp": datetime.now().isoformat()
    }


async def main():
    """Example usage of the sentiment analysis module."""
    location = "Atlanta Beltline"
    results = await analyze_neighborhood_sentiment(location)
    
    print(f"\nud83dudccd Neighborhood Sentiment Analysis for {location}:")
    print(f"Data source: {results['data_source']}")
    print(f"Posts analyzed: {results['posts_analyzed']}")
    print("\nSentiment Summary:")
    print(results["sentiment_summary"])
    
    if results.get("sources"):
        print("\nSources:")
        for i, source in enumerate(results["sources"], 1):
            if source:
                print(f"{i}. {source}")


if __name__ == "__main__":
    asyncio.run(main())
