import pandas as pd
import json
import re
import os

def clean_facebook_listings():
    """
    Reads a JSON file, applies transformations, and saves the cleaned data.

    Transformations:
    - 'price': Extracts only numeric value from price strings (e.g., "$700" → 700).
    - 'laundry_available': Converts 1 → True, 0 → False, and null → None.
    
    Args:
        input_file_path (str): Path to the input JSON file.
        output_file_path (str): Path to save the cleaned JSON file.
    """
    input_file_path = "data/facebook/facebook_listing_transformed.json"
    output_file_path = "data/facebook/facebook_listing_transformed_cleaned.json"
    # **Step 1: Read the JSON File**
    df = pd.read_json(input_file_path)

    # **Step 2: Transform the 'price' Column**
    def extract_price(price):
        """Extract numeric value from price string like '$700' → 700"""
        if isinstance(price, str):
            match = re.search(r'\d+', price)  # Find first number
            return int(match.group()) if match else None
        return None

    df["price"] = df["price"].apply(extract_price)

    # **Step 3: Transform the 'laundry_available' Column**
    def transform_laundry(value):
        """Convert 1 → True, 0 → False, and null → None"""
        if value == 1:
            return True
        elif value == 0:
            return False
        return None  # Keep null as None

    df["laundry_available"] = df["laundry_available"].apply(transform_laundry)

    # **Step 4: Save the Transformed Data Back to JSON**
    df.to_json(output_file_path, orient="records", indent=4)
    
    if os.path.exists(input_file_path):
        os.remove(input_file_path)
        print(f"Old CSV file {input_file_path} deleted.")

    print(f"✅ Cleaned JSON saved to {output_file_path}")

