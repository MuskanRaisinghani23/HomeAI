import configparser
import boto3
import pandas as pd
import re
import json
import time
import logging
from pyspark.sql import SparkSession
from datetime import datetime, timedelta

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airflow.task")

config = configparser.ConfigParser()
config.read('dags/configuration.properties')

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
    # Compile your original pattern
    pattern = re.compile(
        r'^\['
            r'(\d{1,2}/\d{1,2}/\d{2}),\s+'      # date
            r'(\d{1,2}:\d{2}:\d{2})\s+'        # time
            r'(AM|PM)'
        r'\]\s+~\u202f?(.+?):\s+'             # speaker
            r'(.*)$'                           # first line of message
    )

    # Compute cutoff for one week ago
    cutoff = datetime.now() - timedelta(days=2)

    lines = full_text.splitlines()
    lines_rev = lines[::-1]      # start from the bottom (latest message)
    
    data = []
    buffer_lines = []            # to accumulate body lines in reverse

    # keywords to filter (case-insensitive)
    block_pattern = re.compile(r'\b(you removed|plagiarism|assignment|assignments)\b', re.I)

    for line in lines_rev:
        m = pattern.match(line)
        if m:
            # Extract header groups
            date_str, time_str, ampm, speaker, first_msg = m.groups()
            ts = datetime.strptime(f"{date_str}, {time_str} {ampm}", "%m/%d/%y, %I:%M:%S %p")
            
            # If this message is older than one week, stop processing entirely
            if ts < cutoff:
                break

            # Reconstruct the full message body
            body_lines = buffer_lines[::-1]   # reverse to original order
            if body_lines:
                full_msg = first_msg + " " + " ".join(body_lines)
            else:
                full_msg = first_msg

            # skip if it matches any blocked keyword
            if not block_pattern.search(full_msg):
                data.append([ts.strftime("%Y-%m-%d %H:%M:%S"), speaker, full_msg])

            buffer_lines.clear()
        else:
            # Non-header lines belong to the body of the current message
            if line.strip():
                buffer_lines.append(line.strip())

    # Build DataFrame in descending (latest→old) order
    df = pd.DataFrame(data, columns=["timestamp", "speaker", "message"])
    print("-----------------------------------")
    print(f"DataFrame shape: {df.shape}")
    print(f"DataFrame head: {df.head()}")
    print("-----------------------------------")
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

def main():
    s3, bucket = aws_connection()

    unstructured_data_path = config['AWS']['unstructured_data_path'] + "/chat"
    response = s3.list_objects_v2(Bucket=bucket, Prefix=unstructured_data_path)
    
    dfs = []

    for obj in response.get("Contents", []):
        key = obj["Key"]
        print(f"Processing file: {key}")
        if key.lower().endswith(".txt"):
            listings_df = process_s3_file(key, bucket, s3)
            dfs.append(listings_df)

    # combine into a single DataFrame
    if dfs:
        combined_df = pd.concat(dfs, ignore_index=True)
        print(f"Combined DataFrame shape: {combined_df.shape}")
        deduped = (
            combined_df
            .sort_values('timestamp')
            .assign(prefix=lambda d: d['message'].str[:100])    # helper column
            .drop_duplicates(subset=['message'], keep='last')
            .drop(columns=['prefix'])  
        )
        print(f"Deduped DataFrame shape: {deduped.shape}")
        print("Min:", deduped['timestamp'].min())
        print("Max:", deduped['timestamp'].max())
    else:
        combined_df = pd.DataFrame()

    # Save to JSON
    deduped.to_json('data/whatsapp/whatsapp_listings.json', orient='records', indent=4)

    logger.info("Listing extraction completed and saved to JSON.")

    print(f"Saved {len(deduped)} listings to whatsapp_listings.json")

if __name__ == "__main__":
    main()