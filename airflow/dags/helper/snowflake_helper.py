import configparser
import snowflake.connector

config = configparser.ConfigParser()
# config.read('/opt/airflow/dags/load/configuration.properties')
config.read('configuration.properties')

def snowflake_connection():
    try:
        user = config['SNOWFLAKE']['user']
        password = config['SNOWFLAKE']['password']
        account = config['SNOWFLAKE']['account']
        role = config['SNOWFLAKE']['role']
        warehouse = config['SNOWFLAKE']['warehouse']
        database = config['SNOWFLAKE']['database']
        schema = config['SNOWFLAKE']['schema']
        table = config['SNOWFLAKE']['jobsTable']

        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema,
            role=role
        )

        return conn, table
    except Exception as e:
        print("Exception in snowflake_connection function: ",e)
        return   
