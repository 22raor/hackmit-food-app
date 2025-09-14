import time
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def connect_to_existing_chrome():
    """Connect to an existing Chrome instance with remote debugging enabled"""
    chrome_options = Options()
    chrome_options.add_experimental_option("debuggerAddress", "localhost:9222")

    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Error connecting to Chrome: {e}")
        print("Make sure Chrome is running with: chrome --remote-debugging-port=9222")
        return None


def get_restaurant_links(driver, max_restaurants=10):
    """Extract restaurant links from the current DoorDash page"""
    restaurant_links = []

    try:
        # Wait for the page to load
        wait = WebDriverWait(driver, 10)

        # Look for restaurant elements - DoorDash uses various selectors
        # Try multiple possible selectors for restaurant cards
        selectors = [
            'a[href*="/store/"]',
            '[data-anchor-id*="StoreCard"]',
            '[data-testid*="store-card"] a',
            '.store-card a',
            'a[data-testid="store-card"]'
        ]

        restaurant_elements = []
        for selector in selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    restaurant_elements = elements
                    print(f"Found {len(elements)} restaurants using selector: {selector}")
                    break
            except NoSuchElementException:
                continue

        if not restaurant_elements:
            print("No restaurant elements found. The page structure might have changed.")
            return restaurant_links

        # Extract links from the found elements
        for i, element in enumerate(restaurant_elements[:max_restaurants]):
            try:
                link = element.get_attribute('href')
                if link and '/store/' in link:
                    restaurant_links.append(link)
                    print(f"Restaurant {i+1}: {link}")
            except Exception as e:
                print(f"Error extracting link from element {i+1}: {e}")
                continue

        return restaurant_links

    except TimeoutException:
        print("Timeout waiting for page to load")
        return restaurant_links
    except Exception as e:
        print(f"Error extracting restaurant links: {e}")
        return restaurant_links


def save_links_to_file(links, filename="restaurant_links.txt"):
    """Save restaurant links to a text file"""
    try:
        with open(filename, 'w') as f:
            for i, link in enumerate(links, 1):
                f.write(f"{i}. {link}\n")
        print(f"Saved {len(links)} restaurant links to {filename}")
        return True
    except Exception as e:
        print(f"Error saving links to file: {e}")
        return False


def main():
    """Main function to orchestrate the browser scraping"""
    print("Connecting to existing Chrome browser...")

    # Connect to existing Chrome instance
    driver = connect_to_existing_chrome()
    if not driver:
        print("\nTo use this script:")
        print("1. Close all Chrome instances")
        print("2. Start Chrome with: google-chrome --remote-debugging-port=9222")
        print("3. Navigate to a DoorDash restaurant listing page")
        print("4. Run this script again")
        return

    try:
        # Get current URL to verify we're on DoorDash
        current_url = driver.current_url
        print(f"Current page: {current_url}")

        if "doordash.com" not in current_url.lower():
            print("Warning: You don't appear to be on a DoorDash page.")
            print("Please navigate to a DoorDash restaurant listing page first.")
            response = input("Continue anyway? (y/n): ")
            if response.lower() != 'y':
                return

        # Extract restaurant links
        print("\nExtracting restaurant links...")
        links = get_restaurant_links(driver, max_restaurants=10)

        if links:
            # Save links to file
            save_links_to_file(links)
            print(f"\nSuccessfully extracted {len(links)} restaurant links!")
        else:
            print("\nNo restaurant links found. Make sure you're on a DoorDash page with restaurant listings.")

    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        # Don't close the driver since we're connecting to an existing instance
        print("Script completed. Your browser session remains open.")


if __name__ == "__main__":
    main()
