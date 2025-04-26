import os
import logging
import pandas as pd
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType
from snowflake.snowpark import Session
from snowflake.cortex import complete
import configparser

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

def process_listings(json_file_path, output_file_path):
    """Process Facebook listings and extract structured details."""
    connection_params = load_snowflake_config()

    # LLM Prompt
    prompt = """
    I will provide a property listing with multiple attributes. 
    Please extract the following details from the listing and return them in JSON format. If a field is missing or not found, leave the field blank or set it to `null`.
    
    - **Room Count**: The total number of rooms/beds in the property (ROOM_COUNT).
    - **Bathroom Count**: The total number of bathrooms in the property (BATH_COUNT).
    - **People Count**: The total number of people living in the property (PEOPLE_COUNT).
    - **Description**: The short description summary of the property. Translate to English language wherever necessary (DESCRIPTION_summary).
    - **Contact**: The contact number for the listing (CONTACT).
    - **Laundry Availability**: if laundry available then 1 or else 0 (LAUNDARY_AVAILABLE).
    - **Room Type**: Type of room (e.g., Private or Shared) (ROOM_TYPE). Extract this based on Description content.
    - **Other Details**: Any additional details, only if mentioned in the listing. This should be in a dictionary format (OTHER_details).
    
    Ensure the JSON response follows this structure:
    {
      "room_count": number <room_count or null>,
      "bath_count": number <bath_count or null>,
      "people_count": number <people_count or null>,
      "description": string "<description_summary or null>",
      "contact": number "<contact_number or null>",
      "laundry_available": integer (0/1)<laundry_available or null>,
      "room_type": string "<room_type or null>",
      "other_details": dict <other_details_dict or null>
    }
    """

    # Read JSON file
    df_pandas = pd.read_json(json_file_path)
    column_to_process = df_pandas["details"].tolist()

    # Initialize Spark session
    spark = SparkSession.builder.appName("ListingProcessing").getOrCreate()
    df_spark = spark.createDataFrame([(desc,) for desc in column_to_process], ["listing_description"])

    # Define UDF
    @pandas_udf(StringType())
    def transform_description(descriptions: pd.Series) -> pd.Series:
        session = Session.builder.configs(connection_params).create()
        results = []
        for description in descriptions:
            try:
                response = complete(
                    "claude-3-5-sonnet",
                    f"{prompt} \n\n listing description: \n {description}",
                    session=session
                )
                json_data = json.loads(response)
                if "other_details" in json_data:
                    json_data["other_details"] = json.dumps(json_data["other_details"])
                results.append(json.dumps(json_data))
            except Exception as e:
                results.append(json.dumps({"error": str(e)}))
        return pd.Series(results)

    # Apply transformation
    df_transformed = df_spark.withColumn("transformed_description", transform_description("listing_description"))
    transformed_list = df_transformed.select("transformed_description").rdd.flatMap(lambda x: x).collect()
    df_pandas["transformed_description"] = transformed_list
    df_pandas["transformed_description"] = df_pandas["transformed_description"].apply(json.loads)

    # Normalize JSON
    df_transformed_values = pd.json_normalize(df_pandas["transformed_description"])
    df_transformed_values = df_transformed_values.loc[:, ~df_transformed_values.columns.str.contains('other_details.')]
    df_pandas = pd.concat([df_pandas, df_transformed_values], axis=1)

    # Drop unnecessary columns and save
    df_pandas.drop(columns=["transformed_description", "details"], inplace=True)
    df_pandas.to_json(output_file_path, orient="records", indent=4)

    if os.path.exists(json_file_path):
        os.remove(json_file_path)
        logger.info(f"Old JSON file {json_file_path} deleted.")

    logger.info(f"Transformed JSON saved to {output_file_path}")
    spark.stop()

if __name__ == "__main__":
    input_path = "data/facebook/facebook_listing.json"
    output_path = "data/facebook/facebook_listing_transformed.json"
    process_listings(input_path, output_path)
