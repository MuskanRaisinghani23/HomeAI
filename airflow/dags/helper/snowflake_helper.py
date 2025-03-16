import configparser
import snowflake.connector

config = configparser.ConfigParser()
config.read('dags/configuration.properties')
# config.read('configuration.properties')

def snowflake_connection():
    try:
        user = config['snowflake']['user']
        password = config['snowflake']['password']
        account = config['snowflake']['account']
        role = config['snowflake']['role']
        warehouse = config['snowflake']['warehouse']
        database = config['snowflake']['database']
        schema = config['snowflake']['schema']

        conn = snowflake.connector.connect(
            user=user,
            password=password,
            account=account,
            warehouse=warehouse,
            database=database,
            schema=schema,
            role=role
        )

        return conn
    except Exception as e:
        print("Exception in snowflake_connection function: ",e)
        return   