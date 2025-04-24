import configparser
import snowflake.connector

config = configparser.ConfigParser()
config.read('configuration.properties')

def load_snowflake_config() -> dict:
    return {
      "user":     config["snowflake"]["user"],
      "password": config["snowflake"]["password"],
      "account":  config["snowflake"]["account"],
      "role":     config["snowflake"]["role"],
      "warehouse":config["snowflake"]["warehouse"],
      "database": config["snowflake"]["database"],
      "schema":   config["snowflake"]["schema"],
      "insecure_mode":  True,
      "ocsp_fail_open": True,
    }

def snowflake_connection():
    try:
        cfg = load_snowflake_config()
        conn = snowflake.connector.connect(**cfg)
        print("Snowflake connection established successfully.")
        return conn
    except Exception as e:
        print("Exception in snowflake_connection function: ", e)
        return