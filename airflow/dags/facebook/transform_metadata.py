import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("airflow.task")

def transform_metadata_for_city(df):
  try:
    logger.info("Transforming metadata for city")
    logger.info(f"data size {len(df)}")
    df["is_active"] = False
    df["is_loaded"] = False
    df["date_of_listing"] = datetime.now().date()
  except Exception as e:
    logger.error(f"Error transforming metadata for city: {e}")
  
  return df