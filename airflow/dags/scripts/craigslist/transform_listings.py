import os
import logging
import pandas as pd
import json
from snowflake.snowpark import Session
from snowflake.cortex import complete
import configparser
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airflow.task")

def load_snowflake_config():
    """Load Snowflake connection parameters from config file."""
    config = configparser.ConfigParser()
    config.read('dags/configuration.properties')
    return {
        "user": config['snowflake']['user'],
        "password": config['snowflake']['password'],
        "account": config['snowflake']['account'],
        "warehouse": config['snowflake']['warehouse'],
        "database": config['snowflake']['database'],
        "schema": config['snowflake']['schema']
    }

def clean_listings(df):

    def extract_price(price):
        """Extract numeric value from price string like '$700' → 700"""
        if isinstance(price, str):
            cleaned_price = price.replace(',', '')
            match = re.search(r'\d+', cleaned_price)  # Find first number
            return int(match.group()) if match else 0
        return 0
    
    df["price"] = df["Price"].apply(extract_price)

    # **Step 3: Transform the 'laundry_available' Column**
    def transform_laundry(value):
        """Convert 1 → True, 0 → False, and null → None"""
        if value == 1:
            return True
        elif value == 0:
            return False
        return None  # Keep null as None

    df["laundry_available"] = df["laundry_available"].apply(transform_laundry)

    # removing listings with price less than 200
    df = df[df["price"] > 200]
    df.drop(columns=["Price"], inplace=True)

    return df

def process_listings(json_file_path, output_file_path):
    """Process Facebook listings and extract structured details."""
    connection_params = load_snowflake_config()

    # LLM Prompt
    prompt_template = """
    You are a real-estate expert. You excel at analyzing property listing with multiple attributes. 
    Please extract the following details from the listing provided and return them in JSON format. If a field is missing or not found, leave the field blank or set it to `null`.
    
    - **Room Count**: The total number of rooms/beds in the property (ROOM_COUNT).
    - **Bathroom Count**: The total number of bathrooms in the property (BATH_COUNT).
    - **People Count**: The total number of people living in the property (PEOPLE_COUNT).
    - **Contact**: The contact number for the listing (CONTACT).
    - **Laundry Availability**: if laundry available then 1 or else 0 (LAUNDARY_AVAILABLE).
    - **Room Type**: Type of room (e.g., Private or Shared) (ROOM_TYPE).
    - **Main Location**: The main location of the property. Make sure it has both the city and state. State should be abbreviated (e.g., Boston, MA) (MAIN_LOCATION).
    - **Other Details**: Any additional details, only if mentioned in the listing. This should be in a dictionary format (OTHER_details).
    
    Ensure the JSON response follows this structure:
    {{
      "room_count": number <room_count or null>,
      "bath_count": number <bath_count or null>,
      "people_count": number <people_count or null>,
      "contact": number "<contact_number or null>",
      "laundry_available": integer (0/1)<laundry_available or null>,
      "room_type": string "<room_type or null>",
      "main_location": string "<main_location or null>",
      "other_details": dict <other_details_dict or null>
    }}

    Respond ONLY with a valid JSON object. Do not include comments or explanations.

    description: {description}
    more_info: {more_info}
    main_location: {main_location}
    """

    # Read JSON file
    df_pandas = pd.read_json(json_file_path)
    print("----------------------------------")
    print("Listings extracted", df_pandas.shape[0])
    print("----------------------------------")

    session = Session.builder.configs(connection_params).create()

    df_copy = df_pandas.copy()

    # Prepare prompt and complete using Claude
    def extract_structured_data(row) -> dict:
        description = row["Description"]
        more_info = row.get("More Info", None) 
        main_location = row.get("MainLocation", None)

        formatted_prompt = prompt_template.format(description=description, more_info=more_info if more_info else "", main_location=main_location if main_location else "")
        try:
            response = complete(model="claude-3-5-sonnet", prompt=formatted_prompt, session=session)
            structured_data = json.loads(response)
            
            if "other_details" in structured_data and isinstance(structured_data["other_details"], dict):
                structured_data["other_details"] = json.dumps(structured_data["other_details"])  # Store as JSON string
            
            return structured_data
        except Exception as e:
            return {"error": str(e)}

    df_copy["structured"] = df_copy.apply(extract_structured_data, axis=1)

    # Normalize structured output
    df_extracted = pd.json_normalize(df_copy["structured"], sep="_")

    df_extracted["other_details"] = df_copy["structured"].apply(lambda x: json.loads(x["other_details"]) if "other_details" in x else {})
    df_copy = df_copy = df_copy.drop(columns=["structured", "MainLocation", "More Info"])

    flattened_columns = [col for col in df_extracted.columns if col.startswith("other_details.")]
    df_extracted = df_extracted.drop(columns=flattened_columns, errors="ignore")

    df_final = pd.concat([df_copy, df_extracted], axis=1)
    df_final = clean_listings(df_final)

    # Save final output
    df_final.to_json(output_file_path, orient="records", indent=4)

    print(f"Transformed craigslist listings and saved to {output_file_path}")

    if os.path.exists(json_file_path):
        os.remove(json_file_path)
        logger.info(f"Old JSON file {json_file_path} deleted.")

    logger.info(f"Transformed and cleaned JSON saved to {output_file_path}")

def transform_listings():
    """Main function to transform listings."""
    input_path = "data/craigslist/craigslist_listings.json"
    output_path = "data/craigslist/craigslist_listings_cleaned.json"
    process_listings(input_path, output_path)

if __name__ == "__main__":
    transform_listings()
