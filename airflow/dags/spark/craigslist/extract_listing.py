from bs4 import BeautifulSoup
import pandas as pd
import random
import requests
import time
from pyspark.sql import SparkSession
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airflow.task")

def extract_post_details(listing):
    link = listing["url"]

    # Fetch the page content
    response = requests.get(link, headers={"User-Agent": "Mozilla/5.0"})
    if response.status_code != 200:
        print(f"Failed to retrieve page: {response.status_code}")
        return {}

    soup = BeautifulSoup(response.text, 'html.parser')

    # Extract title
    title_element = soup.find('span', id='titletextonly')
    title = title_element.get_text(strip=True) if title_element else 'N/A'

    # Extract location
    location_element = soup.find('div', class_='mapaddress')
    location = location_element.get_text(strip=True) if location_element else 'N/A'

    # Extract attributes
    attributes = []
    attr_groups = soup.find_all('div', class_='attrgroup')
    for group in attr_groups:
        for attr in group.find_all('div'):
            value = attr.find('span', class_='valu')
            if value:
                attributes.append(value.get_text(strip=True))

    # Extract description
    description_element = soup.find('section', id='postingbody')
    if description_element:
        for qr_code_div in description_element.find_all('div', class_='print-information print-qrcode-container'):
            qr_code_div.decompose()
        description = description_element.get_text(separator=" ", strip=True)
    else:
        description = 'N/A'

    # Extract image URL
    image_element = soup.find('img')
    image_url = image_element['src'] if image_element else None

    # Extract posting date
    # date_element = soup.find('time', class_='date timeago')
    # posting_date = date_element['datetime'] if date_element else 'N/A'

    return {
        "Title": title,
        "Location": location,
        "Description": description,
        "More Info": attributes,
        "Image URL": image_url,
        # "Listing Date": posting_date,
        "Listing URL": link,
        "MainLocation": listing["location"],
        "Price": listing["price"]
    }

def scrape_craigslist(city):
    
    base_url = f"https://{city}.craigslist.org/search/roo?postedToday=1#search=2~gallery~0" 

    print(f"Scraping Craigslist for city: {city}")   
    
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.2 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.101 Safari/537.36"
    ]

    # Fetch the page content
    response = requests.get(base_url, headers={'User-Agent': random.choice(user_agents)})
    if response.status_code != 200:
        print(f"Failed to retrieve page: {response.status_code}")
        return []
    soup = BeautifulSoup(response.text, "html.parser")

    listings = []
    post_items = soup.select("li.cl-static-search-result")  # Select all listing elements

    for post in post_items:
        link_tag = post.select_one("a")
        title_tag = post.select_one("div.title")
        price_tag = post.select_one("div.price")
        location_tag = post.select_one("div.location")

        if link_tag and title_tag:
            post_info = {
                "title": title_tag.get_text(strip=True),
                "url": link_tag["href"],
                "price": price_tag.get_text(strip=True) if price_tag else "N/A",
                "location": location_tag.get_text(strip=True) if location_tag else "N/A"
            }
            listings.append(post_info)

    all_listings_details = []
    
    for i, listing in enumerate(listings[:min(len(listings), 15)]):
        details = extract_post_details(listing)  
        all_listings_details.append(details)      
        time.sleep(1)
    
    logger.info(f"Extracted {len(all_listings_details)} listings for city: {city}")

    return all_listings_details

def main():
    # Create a list of cities to scrape
    # cities = ["boston", "sfbay"]
    cities = ["newyork", "chicago", "losangeles", "miami", "austin","detroit","maine",
              "sandiego","houston","dallas","tampa","indianapolis","cleveland","phoenix", "charlotte","atlanta","denver","kansascity",
              "sanantonio","honolulu","nashville","seattle","minneapolis","pittsburgh","neworleans","saltlakecity","buffalo"]
    
    print("---------------------------------------")
    print(cities)
    print("---------------------------------------")

    spark = SparkSession.builder.appName("CraigslistListingExtraction").getOrCreate()
    cities_rdd = spark.sparkContext.parallelize(cities)
    results = cities_rdd.flatMap(scrape_craigslist).collect()

    # Convert to DataFrame
    df = pd.DataFrame(results)

    # Save to JSON
    df.to_json('data/craigslist/craigslist_listings.json', orient='records', indent=4)

    logger.info("Listing extraction completed and saved to JSON.")

    print(f"Saved {len(df)} listings to craigslist_listings.json")

    spark.stop()

if __name__ == "__main__":
    main()