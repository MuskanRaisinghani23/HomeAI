import configparser
from helper.snowflake_helper import snowflake_connection

config = configparser.ConfigParser()
config.read('configuration.properties')

def load_data(file_name, stage_name):
  try:
    conn = snowflake_connection()
    cur = conn.cursor()
    cur.execute(f"PUT file://{file_name} @{stage_name}")
    
    print(f"Data loaded successfully from {file_name} to snowflake stage")
  except Exception as e:
    print("Exception in load_data function: ",e)
    return

def merge_data(stage_name, table_name, filename, primary_key):
  try:
    conn = snowflake_connection()
    cur = conn.cursor()

    merge_query = f'''
    MERGE INTO {table_name} AS t
    USING (SELECT 
                parse_json($1):url LISTING_URL,
                parse_json($1):location LOCATION,
                parse_json($1):price PRICE,
                parse_json($1):room_count ROOM_COUNT,
                parse_json($1):bath_count BATH_COUNT,
                parse_json($1):people_count PEOPLE_COUNT,
                parse_json($1):description DESCRIPTION_SUMMARY,
                parse_json($1):contact CONTACT,
                parse_json($1):laundry_available LAUNDRY_AVAILABLE,
                parse_json($1):img IMAGE_URL,
                parse_json($1):room_type ROOM_TYPE,
                parse_json($1):other_details OTHER_DETAILS
            FROM @{stage_name}/{filename}.gz (FILE_FORMAT => JSON_FORMAT)) AS s    
    ON t.{primary_key} = s.{primary_key} 
    WHEN NOT MATCHED THEN 
        INSERT (listing_url,
                location,
                price,
                listing_date, 
                room_count,
                bath_count,
                people_count,
                description_summary,
                source ,
                contact,
                laundry_available,
                report_count,
                image_url,
                room_type,
                other_details)
        VALUES (s.LISTING_URL,
                s.LOCATION,
                CAST(NULLIF(REGEXP_REPLACE(s.PRICE, '[^0-9.]', ''), '') AS NUMBER),
                CURRENT_DATE,
                CAST(NULLIF(s.ROOM_COUNT, '') AS NUMBER),
                CAST(NULLIF(s.BATH_COUNT, '') AS NUMBER),
                CAST(NULLIF(s.PEOPLE_COUNT, '') AS NUMBER),
                s.DESCRIPTION_SUMMARY,
                'MARKETPLACE',
                s.CONTACT,
                s.LAUNDRY_AVAILABLE,
                0,
                s.IMAGE_URL,
                s.ROOM_TYPE,
                s.OTHER_DETAILS);
    '''
    # print(merge_query)
    print("merging data...")

    # executing load
    cur.execute(merge_query)
    
    print(f"Data merged successfully from {stage_name} to {table_name}")
    
    # Close the cursor and connection
    cur.close()
    conn.close()
      
  except Exception as e:
    print("Exception in merge_data function: ",e)
    return
  
  
def load_to_snowflake():
  file_name = 'facebook_listing_transformed_cleaned.json'
  marketplace_stage_name = 'MARKETPLACE_LISTING_STAGE'
  room_table_name = 'rooms_listings'

  # marketplace data load
  load_data(file_name, marketplace_stage_name)

  merge_data(marketplace_stage_name, room_table_name, file_name, 'LISTING_URL')