import os 
import logging
import pandas as pd
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf
from pyspark.sql.types import StringType
from splinter import Browser
from bs4 import BeautifulSoup as soup
from selenium.webdriver.chrome.options import Options

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airflow.task")

def extract_listing_for_url(url):
    """
    Scrape the listing for the given URL
    """
    try:
        logger.info(f"Processing URL: {url}")

        chrome_options = Options()
        chrome_options.add_argument("--headless")  # Run in headless mode
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        browser = Browser('chrome', options=chrome_options)
        browser.visit(url)

        # Handle pop-ups
        if browser.is_element_present_by_css('div[aria-label="Close"]', wait_time=5):
            logger.info("Closing pop-up")
            browser.find_by_css('div[aria-label="Close"]').first.click()

        browser.execute_script("window.scrollTo(0, 400);")

        # Click the "See More" button if it exists
        try:
            see_more_button = browser.find_by_css('div[role="button"] span.x193iq5w.xeuugli.x13faqbe.x1vvkbs.x1xmvt09.x6prxxf.xvq8zen.x1s688f.xzsf02u')
            if see_more_button:
                see_more_button.click()
            else:
                logger.info("See more button not found")
        except Exception as e:
            logger.warning(f"See more button error: {e}")

        # Parse the HTML
        html = browser.html
        market_soup = soup(html, 'html.parser')

        # Extract relevant data
        div_element = market_soup.find('div', class_='xckqwgs x26u7qi x2j4hbs x78zum5 xnp8db0 x5yr21d x1n2onr6 xh8yej3 xzepove x1stjdt1')
        div_text = div_element.get_text(separator=' ', strip=True) if div_element else ''

        # Close browser
        browser.quit()
        
        return div_text

    except Exception as e:
        logger.error(f"Error processing {url}: {e}")
        return None

def main():
    # Initialize Spark session
    spark = SparkSession.builder.appName("ListingExtraction").getOrCreate()
    extract_listing_udf = udf(extract_listing_for_url, StringType())

    # Step 1: Read CSV using Pandas
    csv_path = "data/facebook/facebook_metadata_raw.csv"
    if not os.path.exists(csv_path):
        logger.error(f"CSV file {csv_path} not found!")
        return

    df_pandas = pd.read_csv(csv_path)
    logger.info("CSV file loaded successfully.")
    
    print(df_pandas.head())

    # Convert Pandas DataFrame to Spark DataFrame
    df_spark = spark.createDataFrame(df_pandas)

    # Step 2: Apply UDF to Extract Metadata
    df_spark = df_spark.withColumn("details", extract_listing_udf(df_spark["url"]))

    # Step 3: Convert Back to Pandas
    df_pandas_transformed = df_spark.toPandas()

    print(df_pandas_transformed.head())

    # Step 4: Save Processed Data
    output_path = "data/facebook/facebook_listing.json"
    df_pandas_transformed.to_json(output_path, orient="records")

    # Step 5: Delete Old CSV File
    if os.path.exists(csv_path):
        os.remove(csv_path)
        logger.info(f"Old CSV file {csv_path} deleted.")

    logger.info("Listing extraction completed and saved to JSON.")

    # Stop Spark session
    spark.stop()

# Ensure the script runs only when executed directly
if __name__ == "__main__":
    main()
