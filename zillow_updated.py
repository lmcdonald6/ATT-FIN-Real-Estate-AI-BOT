from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import pandas as pd
import time
import random

# List of User-Agent strings to randomize
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/94.0.4606.61 Safari/537.36"
]

# Setup WebDriver options
options = webdriver.ChromeOptions()
options.headless = True  # Running in headless mode
options.add_argument(f"user-agent={random.choice(user_agents)}")
driver = webdriver.Chrome(options=options)

try:
    # Target URL
    url = 'https://www.zillow.com'
    driver.get(url)

    # Wait a few seconds for the page to load completely
    time.sleep(random.uniform(3, 7))  # Random delay between 3 to 7 seconds

    # Define WebDriverWait with increased timeout
    wait = WebDriverWait(driver, 120)  # Increase the timeout to 120 seconds if the page is slow to load

    # Use WebDriverWait to ensure elements are loaded
    cards = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, '[data-test="property-card"]')))
    print(f"Found {len(cards)} property cards")

    # Extract details from each property card (limit to 3 results)
    properties = []
    for card in cards[:3]:  # Limit to 3 results
        try:
            price = card.find_element(By.CSS_SELECTOR, '[data-test="property-card-price"]').text
            address = card.find_element(By.CSS_SELECTOR, '[data-test="property-card-addr"]').text

            # Extract additional details
            details_elements = card.find_elements(By.CSS_SELECTOR, '.StyledPropertyCardHomeDetailsList-c11n-8-109-3__sc-1j0som5-0 li')
            details = ' | '.join([detail.text for detail in details_elements])

            properties.append({
                'Price': price,
                'Address': address,
                'Details': details
            })

            # Print extracted data for debugging
            print(f"Extracted data - Price: {price}, Address: {address}, Details: {details}")

        except NoSuchElementException:
            print("Element not found in one of the property cards")

        # Add a random delay between processing each card
        time.sleep(random.uniform(1, 3))  # Random delay between 1 to 3 seconds

    # Ensure at least three results are saved to the CSV file
    if len(properties) < 3:
        print("Less than 3 results found. Please try again.")
    else:
        # Convert data to DataFrame and save to CSV
        df = pd.DataFrame(properties)
        df.to_csv(r'C:\Users\Lewis McDaniel\WHOLESALE\zillow_properties_enhanced.csv', index=False)
        print("Data extraction complete and saved to CSV.")

except TimeoutException:
    print("Timed out waiting for page to load")
    driver.quit()  # Ensure the driver is closed properly

except Exception as e:
    print(f"An error occurred: {e}")
finally:
    driver.quit()