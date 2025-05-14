"""
Neighborhood Sentiment Analysis Module

This module provides functionality to analyze neighborhood sentiment by scraping
Reddit posts and using OpenAI's GPT models to summarize the sentiment.
"""

import asyncio
import os
import logging
from typing import List, Dict, Any, Optional

import openai
from playwright.async_api import async_playwright, Page, Browser
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


async def scrape_reddit_sentiment(query: str, max_posts: int = 10) -> List[Dict[str, str]]:
    """
    Uses Playwright to search Reddit and extract top community sentiment posts.
    
    Args:
        query: The search query for the neighborhood
        max_posts: Maximum number of posts to scrape
        
    Returns:
        List of dictionaries containing post title and content
    """
    results = []
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            
            # Construct search URL for neighborhood reviews
            search_url = f"https://www.reddit.com/search/?q={query.replace(' ', '%20')}+neighborhood+review"
            logger.info(f"Searching Reddit with URL: {search_url}")
            
            await page.goto(search_url)
            await page.wait_for_load_state("networkidle")
            
            # Wait for content to load
            await page.wait_for_timeout(3000)
            
            # Extract posts
            posts = await page.query_selector_all("div[data-testid='post-container']")
            logger.info(f"Found {len(posts)} posts on Reddit")
            
            for i, post in enumerate(posts[:max_posts]):
                try:
                    title_elem = await post.query_selector("h3")
                    title = await title_elem.inner_text() if title_elem else "No title"
                    
                    # Get post URL for reference
                    link_elem = await post.query_selector("a[data-click-id='body']")
                    post_url = await link_elem.get_attribute("href") if link_elem else None
                    if post_url and not post_url.startswith("http"):
                        post_url = f"https://www.reddit.com{post_url}"
                    
                    # Get post content
                    content = await post.inner_text()
                    
                    results.append({
                        "title": title,
                        "content": content,
                        "url": post_url
                    })
                    
                except Exception as e:
                    logger.error(f"Error extracting post {i}: {str(e)}")
                    continue
            
            await browser.close()
    except Exception as e:
        logger.error(f"Error during Reddit scraping: {str(e)}")
    
    return results


def summarize_sentiment_with_gpt(posts: List[Dict[str, str]]) -> str:
    """
    Summarizes the sentiment of Reddit posts using OpenAI's GPT model.
    
    Args:
        posts: List of dictionaries containing post information
        
    Returns:
        Summarized sentiment analysis as a string
    """
    if not posts:
        return "No posts available for sentiment analysis."
    
    # Format posts for the prompt
    formatted_posts = "\n\n".join([
        f"POST TITLE: {post['title']}\nCONTENT: {post['content'][:500]}..." 
        for post in posts
    ])
    
    prompt = f"""
Analyze the sentiment of the following posts from Reddit and summarize how people feel about this neighborhood:

{formatted_posts}

Return a summary with:
1. Overall sentiment (positive, neutral, negative)
2. Key themes mentioned (at least 3-5 themes)
3. Specific positive aspects mentioned
4. Specific concerns or negative aspects mentioned
5. Any notable contradictions in opinions
"""
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are a real estate market analyst specializing in neighborhood sentiment analysis."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=600
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"Error during OpenAI API call: {str(e)}")
        return f"Error generating sentiment summary: {str(e)}"


async def analyze_neighborhood_sentiment(location_query: str, max_posts: int = 10) -> Dict[str, Any]:
    """
    Main function to analyze neighborhood sentiment.
    
    Args:
        location_query: The neighborhood or location to analyze
        max_posts: Maximum number of posts to analyze
        
    Returns:
        Dictionary containing sentiment analysis results
    """
    logger.info(f"Analyzing sentiment for location: {location_query}")
    
    posts = await scrape_reddit_sentiment(location_query, max_posts)
    
    if not posts:
        return {
            "location": location_query,
            "success": False,
            "message": f"No peer reviews found for: {location_query}",
            "posts_analyzed": 0,
            "sentiment_summary": None
        }
    
    summary = summarize_sentiment_with_gpt(posts)
    
    return {
        "location": location_query,
        "success": True,
        "posts_analyzed": len(posts),
        "sentiment_summary": summary,
        "sources": [post.get("url") for post in posts if post.get("url")]
    }


async def main():
    """Example usage of the sentiment analysis module."""
    location = "Atlanta Beltline"
    results = await analyze_neighborhood_sentiment(location)
    
    print(f"\n📍 Neighborhood Sentiment Analysis for {location}:")
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
