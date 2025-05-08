from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.keys import Keys
from scraper_utils import ScraperScheduler
import pandas as pd
import time
import random
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

def scrape_location(location):
    """Scrape Redfin properties for a given location"""
    logger.info(f"Starting search for {location}")
    
    options = webdriver.ChromeOptions()
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--window-size=1920,1080')
    
    driver = None
    try:
        logger.info("Initializing Chrome WebDriver...")
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # Start with the main Redfin page
        logger.info("Accessing Redfin homepage...")
        driver.get('https://www.redfin.com')
        time.sleep(3)
        
        # Find and use the search box
        logger.info("Entering search location...")
        wait = WebDriverWait(driver, 10)
        search_box = wait.until(EC.presence_of_element_located((By.ID, "search-box-input")))
        search_box.clear()
        search_box.send_keys(location)
        time.sleep(2)
        search_box.send_keys(Keys.RETURN)
        
        # Wait for the search results
        logger.info("Waiting for search results...")
        time.sleep(5)
        
        # Wait for property cards
        logger.info("Looking for property listings...")
        wait = WebDriverWait(driver, 30)
        cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.HomeCardContainer')))
        logger.info(f"Found {len(cards)} properties")
        
        properties = []
        for i, card in enumerate(cards[:3], 1):
            try:
                logger.info(f"Processing property {i}/3")
                driver.execute_script("arguments[0].scrollIntoView(true);", card)
                time.sleep(1)
                
                # Extract property details with more flexible selectors
                try:
                    address = card.find_element(By.CSS_SELECTOR, '.homeAddressV2').text
                except:
                    address = card.find_element(By.CSS_SELECTOR, '[data-rf-test-name="searchResult-address"]').text
                    
                try:
                    price = card.find_element(By.CSS_SELECTOR, '.homePriceV2').text
                except:
                    price = card.find_element(By.CSS_SELECTOR, '[data-rf-test-name="searchResult-price"]').text
                
                # Get property stats
                stats = {}
                try:
                    stats_elements = card.find_elements(By.CSS_SELECTOR, '.HomeStatsV2 .stat')
                    for stat in stats_elements:
                        text = stat.text.strip()
                        if 'Beds' in text:
                            stats['Beds'] = text.replace('Beds', '').strip()
                        elif 'Baths' in text:
                            stats['Baths'] = text.replace('Baths', '').strip()
                        elif 'Sq Ft' in text:
                            stats['Square Feet'] = text.replace('Sq Ft', '').strip()
                except:
                    stats_elements = card.find_elements(By.CSS_SELECTOR, '[data-rf-test-name="searchResult-homeStats"] .StandardText')
                    stats = {
                        'Beds': stats_elements[0].text if len(stats_elements) > 0 else "N/A",
                        'Baths': stats_elements[1].text if len(stats_elements) > 1 else "N/A",
                        'Square Feet': stats_elements[2].text if len(stats_elements) > 2 else "N/A"
                    }
                
                property_data = {
                    'Address': address,
                    'Price': price,
                    'Beds': stats.get('Beds', 'N/A'),
                    'Baths': stats.get('Baths', 'N/A'),
                    'Square Feet': stats.get('Square Feet', 'N/A'),
                    'Location': location,
                    'Scrape_Date': time.strftime('%Y-%m-%d')
                }
                properties.append(property_data)
                logger.info(f"Found property: {address} - {price}")
                
            except Exception as e:
                logger.error(f"Error processing property {i}: {str(e)}")
                continue
        
        if properties:
            output_file = r'C:\Users\Lewis McDaniel\WHOLESALE\redfin_properties.csv'
            logger.info(f"Saving {len(properties)} properties to {output_file}")
            
            df = pd.DataFrame(properties)
            try:
                existing_df = pd.read_csv(output_file)
                df = pd.concat([existing_df, df], ignore_index=True)
            except FileNotFoundError:
                logger.info("Creating new CSV file")
                pass
                
            df.to_csv(output_file, index=False)
            logger.info("Data saved successfully")
            return True
            
        logger.warning("No properties found")
        return False
        
    except Exception as e:
        logger.error(f"Error during search: {str(e)}")
        return False
        
    finally:
        if driver:
            driver.quit()
            logger.info("Closed browser session")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("\nUsage: python redfin_scraper.py <location>")
        print("Examples:")
        print("  For ZIP code: python redfin_scraper.py 37218")
        print("  For city/address: python redfin_scraper.py \"Nashville, TN\"")
        sys.exit(1)
        
    location = sys.argv[1]
    scheduler = ScraperScheduler()
    scraper_id = f"redfin_{location}"
    
    if scheduler.can_run(scraper_id):
        if scrape_location(location):
            scheduler.update_last_run(scraper_id)
            logger.info("Search completed successfully!")
        else:
            logger.error("Search failed. Please try again.")
    else:
        wait_time = scheduler.get_wait_time(scraper_id)
        logger.warning(f"Cannot run search yet. {wait_time} until next run.")