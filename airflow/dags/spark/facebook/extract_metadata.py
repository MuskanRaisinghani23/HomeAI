import logging
from splinter import Browser
from bs4 import BeautifulSoup as soup
import pandas as pd
import time
from selenium.webdriver.chrome.options import Options
from pyspark.sql import SparkSession
import os

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airflow.task")

def extract_metadata_for_city(city):
    # Log the start of the function
    logger.info("Setting up Splinter")

    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in headless mode
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    logger.info("Launching the browser")
    browser = Browser('chrome', options=chrome_options)

    # Set up base url
    base_url = f"https://www.facebook.com/marketplace/"

    # Set up search parameters
    days_listed = 1
    query = "room%20for%20rent"

    # Set up full URL
    url = f"{base_url}{city}/search?daysSinceListed={days_listed}&query={query}&exact=false"
    logger.info(f"Visiting URL: {url}")

    # Visit the website
    browser.visit(url)

    # Handle pop-ups
    if browser.is_element_present_by_css('div[aria-label="Close"]', wait_time=10):
        logger.info("Closing pop-up")
        browser.find_by_css('div[aria-label="Close"]').first.click()

    # Scroll down to load more results
    scroll_count = 2
    scroll_delay = 3
    logger.info(f"Scrolling {scroll_count} times with {scroll_delay} seconds delay")

    for _ in range(scroll_count):
        browser.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(scroll_delay)

    # Parse the HTML
    html = browser.html
    market_soup = soup(html, 'html.parser')

    # End the automated browsing session
    logger.info("Closing the browser")
    browser.quit()

    # Extract listings
    logger.info("Extracting listings from the page")
    all_listing = market_soup.find_all('div', class_="x9f619 x78zum5 x1r8uery xdt5ytf x1iyjqo2 xs83m0k x1e558r4 x150jy0e x1iorvi4 xjkvuk6 xnpuxes x291uyu x1uepa24")

    listing_map_list = []
    for listing in all_listing:
        try:
            title = listing.find('span', class_="x1lliihq x6ikm8r x10wlt62 x1n2onr6").text.strip()
            price = listing.find('span', class_="x193iq5w xeuugli x13faqbe x1vvkbs x10flsy6 x1lliihq x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1tu3fi x3x7a5m x1lkfr7t x1lbecb7 x1s688f xzsf02u").text.strip()
            location = listing.find('span', class_="x1lliihq x6ikm8r x10wlt62 x1n2onr6 xlyipyv xuxw1ft").text.strip()
            url = "https://www.facebook.com" + listing.find('a').get('href').split("?")[0]
            img = listing.find('img').get('src')

            listing_map = {
                "title": title,
                "price": price,
                "location": location,
                "url": url,
                'img': img
            }
            listing_map_list.append(listing_map)
        except Exception as e:
            logger.warning(f"Error extracting a listing: {e}")
            continue

    # Convert the results into a DataFrame
    df = pd.DataFrame(listing_map_list)

    # Log the completion of the function
    logger.info(f"Scraping completed, {len(df)} listings found")

    return df

def main():
    # Initialize Spark session
    spark = SparkSession.builder.appName("MetadataExtraction").getOrCreate()

    # Create a list of cities to scrape
    cities = ["boston", "sanfrancisco", "newyork", "chicago", "losangeles", "miami","austin","detroit","portland_maine",
              "sandiego","houston","dallas","tampa","indianapolis","cleveland","phoenix", "charlotte","atlanta","denver","kansascity",
              "sanantonio","honolulu","nashville","seattle","minneapolis","pittsburgh","neworleans","saltlakecity","albuquerque", "buffalo"]

    # Parallelize the scraping task
    cities_rdd = spark.sparkContext.parallelize(cities)

    # Apply the extract_metadata_for_city function to each city in the RDD
    results = cities_rdd.map(extract_metadata_for_city).collect()

    # Combine results into a single DataFrame
    combined_df = pd.concat(results, ignore_index=True)

    # Save the result to a CSV
    combined_df.to_csv('data/facebook/facebook_metadata_raw.csv', index=False)

    # Stop Spark session
    spark.stop()

if __name__ == "__main__":
    main()
