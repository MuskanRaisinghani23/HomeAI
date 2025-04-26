import os
import boto3
import logging
import pandas as pd
import json
import re
from datetime import datetime, timedelta
from pyspark.sql import SparkSession
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import StringType
from snowflake.snowpark import Session
from snowflake.cortex import complete
import configparser

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airflow.task")

def has_contact(msg: str) -> bool:
    phone_regex = re.compile(r'\+?\d[\d\-\s()]{7,}\d')
    return bool(phone_regex.search(msg))

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
    try:
        # LLM Prompt
        prompt = """
        You are a real-estate expert. You excel at analyzing property listing with multiple attributes.
        Please extract the following details from the listing provided and return them in JSON format. If a field is missing or not found, leave the field blank or set it to `null`.

        - **Room Count**: The total number of rooms/beds in the property (ROOM_COUNT).
        - **Bathroom Count**: The total number of bathrooms in the property (BATH_COUNT).
        - **People Count**: The total number of people living in the property (PEOPLE_COUNT).
        - **Contact**: The contact number for the listing (CONTACT).
        - **Laundry Availability**: if laundry available then 1 or else 0 (LAUNDARY_AVAILABLE).
        - **Room Type**: Type of room (e.g., Private or Shared) (ROOM_TYPE).
        - **Price**: The price of the listing (PRICE).
        - **Main Location**: The main location of the property. Make sure it has both the city and state. State should be abbreviated (e.g., Boston, MA) (MAIN_LOCATION).
        - **Description summary**: A brief summary of the listing
        - **Image URL**: Link to any shared images.
        - **Other Details**: Any additional details, only if mentioned in the listing. This should be in a dictionary format (OTHER_details).

        Ensure the JSON response follows this structure:
        {{
        "room_count": number <room_count or null>,
        "bath_count": number <bath_count or null>,
        "people_count": number <people_count or null>,
        "contact": number "<contact_number or null>",
        "laundry_available": integer (0/1)<laundry_available or null>,
        "room_type": string "<room_type or null>",
        "price": number "<price or null>",
        "main_location": string "<main_location or null>",
        "description_summary": string "<description_summary or null>",
        "image_url": string "<image_url or null>",
        "other_details": dict <other_details_dict or null>
        }}

        If the message is about anything other than a job posting, return empty JSON. Also, if contact number is not present, return empty json: {{}}.
        Respond **only** with the JSON—no extra text.

        description: {description}
        """

        # Read JSON file
        deduped_df = pd.read_json(json_file_path)
        print("---------------------------------------")
        print("Dataframe shape: ",deduped_df.shape)
        print("---------------------------------------")

        # only keep rows with a contact number
        deduped_df = deduped_df[deduped_df['message'].apply(has_contact)].reset_index(drop=True)

        # 2) Spin up Spark and parallelize descriptions
        spark = SparkSession.builder.appName("WhatsAppListingProcessing").getOrCreate()
        df_spark = spark.createDataFrame(deduped_df[['message','timestamp']])

        connection_params = load_snowflake_config()
        bc_conf   = spark.sparkContext.broadcast(connection_params)
        bc_prompt = spark.sparkContext.broadcast(prompt)
        
        @pandas_udf(StringType())
        def extract_json(message_batch: pd.Series, ts_batch: pd.Series) -> pd.Series:
            # One Snowflake + LLM session per partition
            cfg     = bc_conf.value
            sess    = Session.builder.configs(cfg).create()
            tmpl    = bc_prompt.value

            out = []
            for msg, ts in zip(message_batch, ts_batch):
                try:
                    resp = complete(
                        "claude-3-5-sonnet",
                        tmpl.format(description=msg),
                        session=sess
                    )
                    data = json.loads(resp)
                    data["date"] = str(ts)
                    out.append(json.dumps(data))
                except Exception as e:
                    out.append(json.dumps({"error": str(e)}))
            return pd.Series(out)

        # 5) Apply the UDF in Spark
        df_transformed = df_spark.withColumn(
            "json_str",
            extract_json("message", "timestamp")
        )

        # 6) Bring results back into pandas
        json_list = df_transformed.select("json_str").rdd.flatMap(lambda x: x).collect()
        results = [json.loads(s) for s in json_list]

        with open(output_file_path, 'w') as f:
            json.dump(results, f, indent=2)

        print("---------------------------------------")
        print(f"output file: {output_file_path}")
        print("---------------------------------------")

        if os.path.exists(json_file_path):
            os.remove(json_file_path)
            logger.info(f"Old JSON file {json_file_path} deleted.")

        logger.info(f"Transformed JSON saved to {output_file_path}")
        spark.stop()

    except Exception as e:
        print("---------------------------------------")
        print(f"Error processing listings: {e}")
        print("---------------------------------------")

if __name__ == "__main__":
    input_path = "data/whatsapp/whatsapp_listings.json"
    output_path = "data/whatsapp/whatsapp_listings_transformed.json"
    process_listings(input_path, output_path)
