# 🤖 DETAILER - Early Stage Agent for Zoning/Permit Scraping
import asyncio
import json
import logging
from playwright.async_api import async_playwright
from openai import OpenAI
import os

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def extract_zoning_info_from_html(html: str) -> dict:
    """Extract zoning and permit information from HTML using GPT-4"""
    try:
        prompt = f"""
Extract zoning and permit info from the following HTML content. Return structured JSON with keys:
- zoning_type: Current zoning designation
- rezoning_activity: Boolean indicating recent rezoning requests
- permit_volume: Estimated monthly permit volume
- recent_applications: List of recent notable applications

HTML:
{html[:2000]}  # Limit content length for token efficiency
"""
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3  # Lower temperature for more consistent output
        )
        
        # Parse the response into a Python dict
        result = json.loads(response.choices[0].message.content)
        logging.info(f"Successfully extracted zoning info: {result}")
        return result
    except Exception as e:
        logging.error(f"Failed to extract zoning info: {str(e)}")
        return {
            "zoning_type": "Unknown",
            "rezoning_activity": False,
            "permit_volume": 0,
            "recent_applications": []
        }

async def scrape_local_building_data(city_url: str) -> dict:
    """Scrape and analyze building department data from city websites"""
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        
        try:
            await page.goto(city_url, timeout=30000)
            content = await page.content()
            
            # Extract structured data using GPT-4
            analysis = extract_zoning_info_from_html(content)
            
            return {
                "url": city_url,
                "analysis": analysis,
                "success": True
            }
            
        except Exception as e:
            logging.error(f"Failed to scrape {city_url}: {str(e)}")
            return {
                "url": city_url,
                "error": str(e),
                "success": False
            }
        finally:
            await browser.close()

# Example usage:
# asyncio.run(scrape_local_building_data("https://chicago.gov/buildings/zoning"))
