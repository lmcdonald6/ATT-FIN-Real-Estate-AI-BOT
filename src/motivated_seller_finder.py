from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service
import pandas as pd
import logging
import random
import time
import os
import signal
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/scraper.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class MotivatedSellerFinder:
    def __init__(self):
        """Initialize the scraper"""
        self.setup_folders()
        self._stop_event = threading.Event()
        self.driver = None
        
    def setup_folders(self):
        """Create necessary folders"""
        os.makedirs('data', exist_ok=True)
        
    def stop(self):
        """Stop the current search"""
        self._stop_event.set()
        if self.driver:
            try:
                self.driver.quit()
            except:
                pass
        logger.info("Search stopped by command")

    def setup_driver(self):
        """Setup Chrome WebDriver with anti-detection measures"""
        if self._stop_event.is_set():
            return None
            
        options = webdriver.ChromeOptions()
        
        # Anti-detection measures
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Random user agent
        user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0'
        ]
        options.add_argument(f'user-agent={random.choice(user_agents)}')
        
        # Additional settings
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-gpu')
        
        # Use WebDriver Manager for automatic chromedriver management
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=options)
        
        # Additional anti-detection
        self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
            'source': '''
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            '''
        })
        return self.driver

    def is_motivated_seller(self, property_data):
        """Check if property matches motivated seller criteria"""
        if self._stop_event.is_set():
            return False
            
        price = property_data.get('price', float('inf'))
        days_on_market = property_data.get('days_on_market', 0)
        price_reduced = property_data.get('price_reduced', False)
        
        # Basic criteria
        if price > 400000:  # Price cap
            return False
            
        # Strong indicators of motivation
        if price_reduced:
            return True
            
        if days_on_market >= 30:  # On market for a while
            return True
            
        # Look for motivated seller keywords in description
        description = property_data.get('description', '').lower()
        motivated_keywords = [
            'price reduced', 'reduced', 'must sell', 'motivated', 
            'as-is', 'as is', 'fixer', 'needs work', 'cash only',
            'vacant', 'estate sale', 'foreclosure', 'short sale'
        ]
        
        if any(keyword in description for keyword in motivated_keywords):
            return True
            
        return False

    def extract_property_data(self, card):
        """Extract all relevant property data from a card"""
        if self._stop_event.is_set():
            return None
            
        try:
            # Basic info with multiple selector attempts
            address = None
            for selector in ['.homeAddressV2', '[data-rf-test-name="searchResult-address"]']:
                try:
                    address = card.find_element(By.CSS_SELECTOR, selector).text
                    break
                except NoSuchElementException:
                    continue
                    
            if not address:
                raise Exception("Could not find address")
                
            # Get price
            price_elem = None
            for selector in ['.homePriceV2', '[data-rf-test-name="searchResult-price"]']:
                try:
                    price_elem = card.find_element(By.CSS_SELECTOR, selector)
                    break
                except NoSuchElementException:
                    continue
                    
            if not price_elem:
                raise Exception("Could not find price")
                
            price = int(price_elem.text.replace('$', '').replace(',', '').split()[0])
            
            # Get property details
            details = {}
            stats = card.find_elements(By.CSS_SELECTOR, '.HomeStatsV2 .stat, [data-rf-test-name="searchResult-homeStats"] .StandardText')
            for stat in stats:
                text = stat.text.lower()
                if 'bed' in text:
                    details['beds'] = text.split()[0]
                elif 'bath' in text:
                    details['baths'] = text.split()[0]
                elif 'sq ft' in text:
                    details['square_feet'] = text.split()[0].replace(',', '')
                    
            # Get full description and check for price reduction
            description = card.text.lower()
            price_reduced = any(kw in description for kw in [
                'price reduced', 'reduced', 'new price', 
                'price improvement', 'reduced price'
            ])
            
            # Extract days on market
            days_on_market = 0
            if 'days on' in description:
                try:
                    days_text = description.split('days on')[0].strip().split()[-1]
                    days_on_market = int(days_text)
                except:
                    pass
                    
            return {
                'address': address,
                'price': price,
                'beds': details.get('beds', 'N/A'),
                'baths': details.get('baths', 'N/A'),
                'square_feet': details.get('square_feet', 'N/A'),
                'price_reduced': price_reduced,
                'days_on_market': days_on_market,
                'description': description
            }
            
        except Exception as e:
            logger.error(f"Error extracting property data: {str(e)}")
            return None

    def search_properties(self, location):
        """Search for properties in a location"""
        if self._stop_event.is_set():
            return []
            
        self.driver = self.setup_driver()
        if not self.driver:
            return []
            
        properties = []
        
        try:
            logger.info(f"Searching {location}")
            self.driver.get('https://www.redfin.com')
            time.sleep(random.uniform(2, 4))
            
            if self._stop_event.is_set():
                return properties
                
            # Find and use search box
            try:
                search_box = WebDriverWait(self.driver, 15).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "input[data-rf-test-name='search-input'], #search-box-input"))
                )
                search_box.clear()
                
                # Type like a human
                for char in location:
                    if self._stop_event.is_set():
                        return properties
                    search_box.send_keys(char)
                    time.sleep(random.uniform(0.1, 0.3))
                    
                time.sleep(random.uniform(1, 2))
                search_box.send_keys(Keys.RETURN)
                logger.info("Submitted search")
                time.sleep(random.uniform(4, 6))
                
            except Exception as e:
                logger.error(f"Failed to enter search location: {str(e)}")
                return properties
                
            if self._stop_event.is_set():
                return properties
                
            # Find property cards with multiple selector attempts
            selectors = [
                '.HomeCardContainer',
                '[data-rf-test-name="SearchResultItem"]',
                '.HomeCard',
                '.SearchResultItem'
            ]
            
            cards = None
            for selector in selectors:
                if self._stop_event.is_set():
                    return properties
                try:
                    cards = WebDriverWait(self.driver, 15).until(
                        EC.presence_of_all_elements_located((By.CSS_SELECTOR, selector))
                    )
                    if cards:
                        logger.info(f"Found {len(cards)} properties using selector: {selector}")
                        break
                except:
                    continue
                    
            if not cards:
                logger.error("Could not find any property cards")
                return properties
                
            # Process each property
            for i, card in enumerate(cards, 1):
                if self._stop_event.is_set():
                    return properties
                    
                try:
                    logger.info(f"Processing property {i}/{len(cards)}")
                    
                    # Scroll to card
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", card)
                    time.sleep(random.uniform(0.5, 1))
                    
                    property_data = self.extract_property_data(card)
                    if property_data and self.is_motivated_seller(property_data):
                        property_data['location'] = location
                        properties.append(property_data)
                        logger.info(f"Found motivated seller: {property_data['address']} - ${property_data['price']:,}")
                        
                except Exception as e:
                    logger.error(f"Error processing property {i}: {str(e)}")
                    continue
                    
        except Exception as e:
            logger.error(f"Error during search: {str(e)}")
        finally:
            try:
                if self.driver:
                    self.driver.quit()
                    self.driver = None
                logger.info("Browser closed successfully")
            except:
                logger.warning("Failed to close browser properly")
            
        return properties

    def save_results(self, properties):
        """Save results to CSV"""
        if not properties:
            logger.info("No motivated sellers found")
            return
            
        output_file = 'data/motivated_sellers.csv'
        df = pd.DataFrame(properties)
        
        # Update existing data
        try:
            existing_df = pd.read_csv(output_file)
            df = pd.concat([existing_df, df]).drop_duplicates(subset=['address'], keep='last')
        except FileNotFoundError:
            pass
            
        df.to_csv(output_file, index=False)
        logger.info(f"Saved {len(properties)} properties to {output_file}")

    def run(self, location):
        """Main execution method"""
        self._stop_event.clear()  # Reset stop flag
        logger.info(f"Starting search in {location}")
        properties = self.search_properties(location)
        self.save_results(properties)
        return properties

def signal_handler(sig, frame):
    finder.stop()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    finder = MotivatedSellerFinder()
    finder.run('37218')
