import configparser
import boto3
import pandas as pd
import re
from snowflake.snowpark import Session
from snowflake.cortex import complete
import json

config = configparser.ConfigParser()
config.read('../configuration.properties')

prompt_template = """
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

phone_regex = re.compile(r'\+?\d[\d\-\s()]{7,}\d')
def has_contact(msg: str) -> bool:
    return bool(phone_regex.search(msg))

def load_snowflake_config():
    """Load Snowflake connection parameters from config file."""
    return {
        "user": config['snowflake']['user'],
        "password": config['snowflake']['password'],
        "account": config['snowflake']['account'],
        "warehouse": config['snowflake']['warehouse'],
        "database": config['snowflake']['database'],
        "schema": config['snowflake']['schema']
    }

def aws_connection():
    try:
        aws_access_key = config['AWS']['access_key']
        aws_secret_key = config['AWS']['secret_key']
        bucket_name = config['AWS']['bucket']

        s3_client = boto3.client(
            's3', aws_access_key_id=aws_access_key, aws_secret_access_key=aws_secret_key)

        return s3_client, bucket_name

    except Exception as e:
        print("Exception in aws_connection function: ", e)
        return

def split_chat_to_dataframe(full_text):
    lines= full_text.splitlines()
    pattern = re.compile(
        r'^\['
            r'(\d{1,2}/\d{1,2}/\d{2}),\s+'
            r'(\d{1,2}:\d{2}:\d{2})\s+(AM|PM)'
        r'\]\s+~\u202f?(.+?):\s+(.*)$'  
    )
    data = []

    for line in lines:
        m = pattern.match(line)
        if m:
            date, time, ampm, speaker, msg = m.groups()
            timestamp = f"{date}, {time} {ampm}"
            data.append([timestamp, speaker, msg])
        else:
            if data:
                data[-1][2] += " " + line.strip()

    df = pd.DataFrame(data, columns=["timestamp", "speaker", "message"])
    return df
    
def process_s3_file(key: str, bucket, s3):
    """
    Reads a .txt from S3, grabs the full content,
    and runs one Cortex extraction on the entire blob.
    """
    obj = s3.get_object(Bucket=bucket, Key=key)
    full_text = obj["Body"].read().decode("utf-8")
    if not full_text.strip():
        print(f"[{key}] empty, skipping")
        return

    listings_df = split_chat_to_dataframe(full_text)

    return listings_df

def get_structured_data(message, session, prompt_template) -> dict:

    if not has_contact(message):
        return {}       

    formatted_prompt = prompt_template.format(description=message)
    try:
        response = complete(model="claude-3-5-sonnet", prompt=formatted_prompt, session=session)
        structured_data = json.loads(response)
        
        return structured_data
    except Exception as e:
        return {"error": str(e)}
    
def main():
    s3, bucket = aws_connection()
    connection_params = load_snowflake_config()
    session = Session.builder.configs(connection_params).create()

    unstructured_data_path = config['AWS']['unstructured_data_path'] + "/chat"
    structured_data_path = config['AWS']['structured_data_path']
    
    response = s3.list_objects_v2(Bucket=bucket, Prefix=unstructured_data_path)
    for obj in response.get("Contents", []):
        key = obj["Key"]
        print(f"Processing file: {key}")
        if key.lower().endswith(".txt"):
            listings_df = process_s3_file(key, bucket, s3)
            df = listings_df.copy()
            if df is not None:
                df['timestamp'] = pd.to_datetime(
                    df['timestamp'],
                    format="%m/%d/%y, %I:%M:%S %p"
                )
                deduped = (
                    df
                    .sort_values('timestamp')
                    .drop_duplicates(subset=['message'], keep='last')
                )
                results = []
                for msg in deduped['message']:
                    structured = get_structured_data(msg, session, prompt_template)

                    if structured:
                        structured['date'] = str(deduped.loc[deduped['message'] == msg, 'timestamp'].values[0])
                        results.append(structured)
                
                out_filename = key.rsplit('/', 1)[-1].replace('.txt', '.json')

                # with open(out_filename, 'w') as f:
                #     json.dump(results, f, indent=2)
                # print(f"output file: {out_filename}")

                # Upload to S3
                out_key = f"{structured_data_path}/{out_filename}"
                s3.put_object(
                    Bucket=bucket,
                    Key=out_key,
                    Body=json.dumps(results, indent=2)
                )
                print(f"  → Uploaded to S3: {bucket}/{out_key}")
                
        break
    session.close()

if __name__ == "__main__":
    main()