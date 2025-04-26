import configparser
from helper.snowflake_helper import snowflake_connection
import os

config = configparser.ConfigParser()
config.read('configuration.properties')

def load_data(file_name, stage_name):
  try:
    conn = snowflake_connection()
    cur = conn.cursor()
    put_command = f"PUT file://{file_name} @{stage_name} AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
    print(put_command)
    result = cur.execute(put_command).fetchall()
    print("PUT command result: ", result)
    print(f"Data loaded successfully from {file_name} to snowflake stage")
    cur.close()
    conn.close()
  except Exception as e:
    print("Exception in load_data function: ",e)
    return

def merge_data(stage_name, table_name, filename):
  try:
    conn = snowflake_connection()
    cur = conn.cursor()

    merge_query = f'''
    MERGE INTO {table_name} AS t
    USING (SELECT 
                parse_json($1):main_location LOCATION,
                parse_json($1):price PRICE,
                parse_json($1):date listing_date,
                parse_json($1):room_count ROOM_COUNT,
                parse_json($1):bath_count BATH_COUNT,
                parse_json($1):people_count PEOPLE_COUNT,
                parse_json($1):description_summary DESCRIPTION_SUMMARY,
                parse_json($1):contact CONTACT,
                parse_json($1):laundry_available LAUNDRY_AVAILABLE,
                parse_json($1):image_url IMAGE_URL,
                parse_json($1):room_type ROOM_TYPE,
                parse_json($1):other_details OTHER_DETAILS
            FROM @{stage_name}/{filename}.gz (FILE_FORMAT => JSON_FORMAT)) AS s    
    ON RIGHT( REGEXP_REPLACE(t.contact, '[^0-9]', ''), 10 ) = RIGHT( REGEXP_REPLACE(s.contact, '[^0-9]', ''), 10 ) AND t.location = s.location AND t.price = s.price
    WHEN NOT MATCHED THEN 
        INSERT (LISTING_URL,
                location,
                price,
                listing_date, 
                room_count,
                bath_count,
                people_count,
                description_summary,
                source,
                contact,
                laundry_available,
                report_count,
                image_url,
                room_type,
                other_details,
                room_id)
        VALUES (null,
                s.LOCATION,
                CAST(NULLIF(REGEXP_REPLACE(s.PRICE, '[^0-9.]', ''), '') AS NUMBER),
                COALESCE(s.LISTING_DATE, CURRENT_DATE()),
                CAST(NULLIF(s.ROOM_COUNT, '') AS NUMBER),
                CAST(NULLIF(s.BATH_COUNT, '') AS NUMBER),
                CAST(NULLIF(s.PEOPLE_COUNT, '') AS NUMBER),
                s.DESCRIPTION_SUMMARY,
                'WHATSAPP',
                s.CONTACT,
                s.LAUNDRY_AVAILABLE,
                0,
                s.IMAGE_URL,
                s.ROOM_TYPE,
                s.OTHER_DETAILS,
                rooms_listings_seq.nextval);
    '''
    print(merge_query)
    print("merging data...")

    # executing load
    print(merge_query)
    cur.execute(merge_query)
    
    print(f"Data merged successfully from {stage_name} to {table_name}")
    
    # Close the cursor and connection
    cur.close()
    conn.close()
      
  except Exception as e:
    print("Exception in merge_data function: ",e)
    return
  
  
def load_to_snowflake():
  current_directory = os.path.dirname(os.path.realpath(__file__))
  print("path +++++++++++++++++", current_directory)
  file_name = 'data/whatsapp/whatsapp_listings_transformed.json'
  stage_file_name = 'whatsapp_listings_transformed.json'
  whatsapp_stage_name = 'WHATSAPP_LISTING_STAGE'
  room_table_name = 'rooms_listings'

  # whatsapp data load
  load_data(file_name, whatsapp_stage_name)

  merge_data(whatsapp_stage_name, room_table_name, stage_file_name)