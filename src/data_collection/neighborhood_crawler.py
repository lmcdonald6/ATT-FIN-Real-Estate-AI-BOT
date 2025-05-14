"""
Neighborhood Sentiment Crawler

This module implements a data collection service that crawls various sources
for neighborhood sentiment data and stores it in a local database for later analysis.
This reduces reliance on external APIs and builds a proprietary data asset.
"""

import asyncio
import json
import logging
import os
import re
import sqlite3
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from urllib.parse import quote_plus

from playwright.async_api import async_playwright, Page, Browser

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 
                      'data', 'neighborhood_data.db')


class NeighborhoodCrawler:
    """Crawler that collects neighborhood sentiment data from various sources."""
    
    def __init__(self, db_path: str = DB_PATH):
        """
        Initialize the neighborhood crawler.
        
        Args:
            db_path: Path to the SQLite database for storing crawled data
        """
        self.db_path = db_path
        self._ensure_db_exists()
    
    def _ensure_db_exists(self):
        """
        Ensure the database and required tables exist.
        """
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables if they don't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS neighborhood_posts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            neighborhood TEXT NOT NULL,
            source TEXT NOT NULL,
            title TEXT,
            content TEXT NOT NULL,
            url TEXT,
            post_date TEXT,
            crawl_date TEXT NOT NULL,
            metadata TEXT
        )
        ''')
        
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS neighborhood_cache (
            neighborhood TEXT PRIMARY KEY,
            data TEXT NOT NULL,
            last_updated TEXT NOT NULL
        )
        ''')
        
        conn.commit()
        conn.close()
        
        logger.info(f"Database initialized at {self.db_path}")
    
    async def crawl_reddit(self, neighborhood: str, max_posts: int = 15) -> List[Dict[str, Any]]:
        """
        Crawl Reddit for posts about a specific neighborhood.
        
        Args:
            neighborhood: The neighborhood to search for
            max_posts: Maximum number of posts to collect
            
        Returns:
            List of dictionaries containing post data
        """
        results = []
        search_terms = [
            f"{neighborhood} neighborhood review",
            f"{neighborhood} living",
            f"moving to {neighborhood}"
        ]
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
                
                for search_term in search_terms:
                    page = await context.new_page()
                    encoded_term = quote_plus(search_term)
                    search_url = f"https://www.reddit.com/search/?q={encoded_term}&sort=relevance"
                    
                    logger.info(f"Crawling Reddit with search term: {search_term}")
                    
                    try:
                        await page.goto(search_url, timeout=30000)
                        await page.wait_for_load_state("networkidle", timeout=10000)
                        
                        # Wait for posts to load
                        await page.wait_for_timeout(3000)
                        
                        # Extract posts
                        posts = await page.query_selector_all("div[data-testid='post-container']")
                        logger.info(f"Found {len(posts)} posts for search term: {search_term}")
                        
                        for post in posts[:max_posts // len(search_terms)]:
                            try:
                                # Extract title
                                title_elem = await post.query_selector("h3")
                                title = await title_elem.inner_text() if title_elem else "No title"
                                
                                # Extract URL
                                link_elem = await post.query_selector("a[data-click-id='body']")
                                post_url = await link_elem.get_attribute("href") if link_elem else None
                                if post_url and not post_url.startswith("http"):
                                    post_url = f"https://www.reddit.com{post_url}"
                                
                                # Extract content preview
                                content = await post.inner_text()
                                
                                # Only add if the post seems relevant
                                if neighborhood.lower() in title.lower() or neighborhood.lower() in content.lower():
                                    results.append({
                                        "neighborhood": neighborhood,
                                        "source": "reddit",
                                        "title": title,
                                        "content": content,
                                        "url": post_url,
                                        "post_date": None,  # Reddit doesn't show exact dates in search
                                        "crawl_date": datetime.now().isoformat(),
                                        "metadata": json.dumps({"search_term": search_term})
                                    })
                            except Exception as e:
                                logger.error(f"Error extracting Reddit post: {str(e)}")
                                continue
                    except Exception as e:
                        logger.error(f"Error during Reddit search for '{search_term}': {str(e)}")
                    finally:
                        await page.close()
                
                await browser.close()
        except Exception as e:
            logger.error(f"Error during Reddit crawling: {str(e)}")
        
        return results
    
    async def crawl_city_data(self, neighborhood: str, city: str = None) -> List[Dict[str, Any]]:
        """
        Crawl City-Data forums for posts about a specific neighborhood.
        
        Args:
            neighborhood: The neighborhood to search for
            city: The city containing the neighborhood (optional)
            
        Returns:
            List of dictionaries containing post data
        """
        results = []
        search_term = f"{neighborhood} {city if city else ''}".strip()
        
        try:
            async with async_playwright() as p:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
                )
                page = await context.new_page()
                
                # City-Data search URL
                encoded_term = quote_plus(search_term)
                search_url = f"https://www.city-data.com/forum/search.php?do=process&query={encoded_term}&titleonly=0"
                
                logger.info(f"Crawling City-Data forums for: {search_term}")
                
                try:
                    await page.goto(search_url, timeout=30000)
                    await page.wait_for_load_state("networkidle", timeout=10000)
                    
                    # Extract search results
                    result_items = await page.query_selector_all("li.searchresult")
                    logger.info(f"Found {len(result_items)} City-Data forum results for: {search_term}")
                    
                    for item in result_items[:10]:  # Limit to 10 results
                        try:
                            # Extract title and URL
                            title_elem = await item.query_selector("div.title a")
                            title = await title_elem.inner_text() if title_elem else "No title"
                            post_url = await title_elem.get_attribute("href") if title_elem else None
                            
                            # Extract preview content
                            content_elem = await item.query_selector("div.searchresult")
                            content = await content_elem.inner_text() if content_elem else ""
                            
                            # Extract date if available
                            date_elem = await item.query_selector("div.searchmeta")
                            date_text = await date_elem.inner_text() if date_elem else ""
                            post_date = None
                            date_match = re.search(r'\d{2}-\d{2}-\d{4}', date_text)
                            if date_match:
                                post_date = date_match.group(0)
                            
                            results.append({
                                "neighborhood": neighborhood,
                                "source": "city-data",
                                "title": title,
                                "content": content,
                                "url": post_url,
                                "post_date": post_date,
                                "crawl_date": datetime.now().isoformat(),
                                "metadata": json.dumps({"search_term": search_term})
                            })
                        except Exception as e:
                            logger.error(f"Error extracting City-Data post: {str(e)}")
                            continue
                except Exception as e:
                    logger.error(f"Error during City-Data search: {str(e)}")
                finally:
                    await page.close()
                    await browser.close()
        except Exception as e:
            logger.error(f"Error during City-Data crawling: {str(e)}")
        
        return results
    
    def store_posts(self, posts: List[Dict[str, Any]]):
        """
        Store crawled posts in the database.
        
        Args:
            posts: List of post dictionaries to store
        """
        if not posts:
            logger.info("No posts to store")
            return
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for post in posts:
            cursor.execute('''
            INSERT INTO neighborhood_posts 
            (neighborhood, source, title, content, url, post_date, crawl_date, metadata)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                post["neighborhood"],
                post["source"],
                post["title"],
                post["content"],
                post["url"],
                post["post_date"],
                post["crawl_date"],
                post["metadata"]
            ))
        
        conn.commit()
        conn.close()
        
        logger.info(f"Stored {len(posts)} posts in the database")
    
    def get_stored_posts(self, neighborhood: str, max_age_days: int = 30) -> List[Dict[str, Any]]:
        """
        Retrieve stored posts for a neighborhood from the database.
        
        Args:
            neighborhood: The neighborhood to get posts for
            max_age_days: Maximum age of posts to retrieve in days
            
        Returns:
            List of post dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # This enables column access by name
        cursor = conn.cursor()
        
        # Calculate the cutoff date
        cutoff_date = (datetime.now() - timedelta(days=max_age_days)).isoformat()
        
        cursor.execute('''
        SELECT * FROM neighborhood_posts
        WHERE neighborhood = ? AND crawl_date > ?
        ORDER BY crawl_date DESC
        ''', (neighborhood, cutoff_date))
        
        rows = cursor.fetchall()
        posts = [dict(row) for row in rows]
        
        conn.close()
        
        logger.info(f"Retrieved {len(posts)} posts for {neighborhood} from database")
        return posts
    
    async def crawl_neighborhood(self, neighborhood: str, city: str = None, force_refresh: bool = False) -> List[Dict[str, Any]]:
        """
        Crawl multiple sources for neighborhood data and store the results.
        
        Args:
            neighborhood: The neighborhood to crawl for
            city: The city containing the neighborhood (optional)
            force_refresh: Whether to force a fresh crawl even if recent data exists
            
        Returns:
            List of all posts found across sources
        """
        # Check if we have recent data unless force_refresh is True
        if not force_refresh:
            existing_posts = self.get_stored_posts(neighborhood)
            if existing_posts:
                logger.info(f"Using {len(existing_posts)} existing posts for {neighborhood}")
                return existing_posts
        
        # Crawl from multiple sources
        reddit_posts = await self.crawl_reddit(neighborhood)
        city_data_posts = await self.crawl_city_data(neighborhood, city)
        
        # Combine results
        all_posts = reddit_posts + city_data_posts
        
        # Store in database
        self.store_posts(all_posts)
        
        return all_posts


async def main():
    """
    Example usage of the neighborhood crawler.
    """
    crawler = NeighborhoodCrawler()
    
    # Example neighborhoods to crawl
    neighborhoods = [
        ("Atlanta Beltline", "Atlanta"),
        ("Midtown", "Manhattan"),
        ("Mission District", "San Francisco")
    ]
    
    for neighborhood, city in neighborhoods:
        print(f"\nCrawling data for {neighborhood}, {city}...")
        posts = await crawler.crawl_neighborhood(neighborhood, city)
        
        print(f"Found {len(posts)} posts for {neighborhood}")
        if posts:
            print("Sample titles:")
            for post in posts[:3]:  # Show first 3 post titles
                print(f"- {post['title']}")


if __name__ == "__main__":
    asyncio.run(main())
