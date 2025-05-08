"""Enhanced Redfin scraper with anti-detection measures"""
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
import pandas as pd
import time
import random
import logging
from datetime import datetime
from typing import List, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/redfin_scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def setup_driver():
    """Setup Chrome driver with anti-detection measures"""
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
    options.add_experimental_option('useAutomationExtension', False)
    
    # Add random user agent
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Edge/120.0.0.0'
    ]
    options.add_argument(f'user-agent={random.choice(user_agents)}')
    
    driver = webdriver.Chrome(options=options)
    driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    
    return driver

async def search_properties(zip_code: str, max_price: Optional[int] = None, min_beds: Optional[int] = None) -> List[Dict]:
    """Search properties with retry logic"""
    logger.info(f"Starting search for ZIP code {zip_code}")
    
    driver = None
    try:
        driver = setup_driver()
        
        # Start with the main Redfin page
        logger.info("Accessing Redfin homepage...")
        driver.get('https://www.redfin.com')
        time.sleep(random.uniform(2, 4))
        
        # Find and use the search box
        logger.info("Entering search location...")
        wait = WebDriverWait(driver, 10)
        search_box = wait.until(EC.presence_of_element_located((By.ID, "search-box-input")))
        search_box.clear()
        search_box.send_keys(zip_code)
        time.sleep(random.uniform(1, 2))
        search_box.send_keys(Keys.RETURN)
        
        # Wait for the search results
        logger.info("Waiting for search results...")
        time.sleep(random.uniform(3, 5))
        
        # Apply filters if provided
        if max_price or min_beds:
            logger.info("Applying filters...")
            # TODO: Implement filter application logic
            pass
        
        # Wait for property cards with retry
        logger.info("Looking for property listings...")
        max_retries = 3
        retry_count = 0
        cards = None
        
        while retry_count < max_retries:
            try:
                wait = WebDriverWait(driver, 15)
                cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.HomeCardContainer')))
                break
            except:
                retry_count += 1
                if retry_count < max_retries:
                    delay = 5 * (2 ** retry_count) + random.uniform(1, 3)
                    logger.info(f"Retrying in {delay:.1f} seconds...")
                    time.sleep(delay)
        
        if not cards:
            logger.warning("No property cards found")
            return []
            
        logger.info(f"Found {len(cards)} properties")
        
        properties = []
        for i, card in enumerate(cards[:10], 1):  # Limit to first 10 properties
            try:
                logger.info(f"Processing property {i}/10")
                driver.execute_script("arguments[0].scrollIntoView(true);", card)
                time.sleep(random.uniform(0.5, 1))
                
                # Extract property details with flexible selectors
                try:
                    address = card.find_element(By.CSS_SELECTOR, '.homeAddressV2').text
                except:
                    address = card.find_element(By.CSS_SELECTOR, '[data-rf-test-name="searchResult-address"]').text
                    
                try:
                    price_text = card.find_element(By.CSS_SELECTOR, '.homePriceV2').text
                except:
                    price_text = card.find_element(By.CSS_SELECTOR, '[data-rf-test-name="searchResult-price"]').text
                price = int(price_text.replace("$", "").replace(",", ""))
                
                # Get property stats
                stats = {}
                try:
                    stats_elements = card.find_elements(By.CSS_SELECTOR, '.HomeStatsV2 .stat')
                    for stat in stats_elements:
                        text = stat.text.strip()
                        if 'Beds' in text:
                            stats['beds'] = int(text.replace('Beds', '').strip())
                        elif 'Sq Ft' in text:
                            stats['square_feet'] = int(text.replace('Sq Ft', '').strip().replace(',', ''))
                except:
                    stats_elements = card.find_elements(By.CSS_SELECTOR, '[data-rf-test-name="searchResult-homeStats"] .StandardText')
                    stats = {
                        'beds': int(stats_elements[0].text.split()[0]) if len(stats_elements) > 0 else None,
                        'square_feet': int(stats_elements[2].text.split()[0].replace(',', '')) if len(stats_elements) > 2 else None
                    }
                
                # Check if price reduced
                try:
                    price_reduced = card.find_element(By.CSS_SELECTOR, ".PriceReduction").is_displayed()
                except:
                    price_reduced = False
                
                # Get listing URL
                try:
                    listing_url = card.find_element(By.CSS_SELECTOR, "a.slider-item").get_attribute("href")
                except:
                    listing_url = None
                
                property_data = {
                    'address': address,
                    'price': price,
                    'beds': stats.get('beds'),
                    'square_feet': stats.get('square_feet'),
                    'price_reduced': price_reduced,
                    'listing_url': listing_url,
                    'source': 'redfin',
                    'last_updated': datetime.now().isoformat()
                }
                
                properties.append(property_data)
                logger.info(f"Found property: {address} - ${price:,}")
                
            except Exception as e:
                logger.error(f"Error processing property {i}: {str(e)}")
                continue
                
            # Random delay between properties
            if i < len(cards[:10]):
                time.sleep(random.uniform(0.5, 1.5))
        
        return properties
        
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        return []
        
    finally:
        if driver:
            driver.quit()
            logger.info("Closed browser session")
