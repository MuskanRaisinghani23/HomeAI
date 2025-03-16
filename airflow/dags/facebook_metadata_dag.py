from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy_operator import DummyOperator 
from airflow.utils.dates import days_ago
import os

from scripts.facebook.load_data import load_to_snowflake
from scripts.facebook.transform_data import clean_facebook_listings

current_directory = os.path.dirname(os.path.realpath(__file__))
extract_metadata = os.path.join(current_directory, 'spark', 'facebook','extract_metadata.py')
extract_listing = os.path.join(current_directory, 'spark', 'facebook','extract_listing.py')
transform_listing = os.path.join(current_directory, 'spark', 'facebook','transform_listing.py')


dag = DAG(
  dag_id="facebook_marketplace_scraper",
  schedule_interval="0 22 * * *",
  start_date=days_ago(0),
  catchup=False,
  dagrun_timeout=timedelta(minutes=360),
  max_active_runs=4
)

# Start Task
start_task = DummyOperator(task_id='start', dag=dag)

spark_extract_metadata_task = SparkSubmitOperator(
  task_id='extract_listing_metadata',
  application=extract_metadata,
  conn_id='spark_default', 
  conf={'spark.master': 'spark://spark-master:7077'},
  dag=dag
)

spark_extract_listing_task = SparkSubmitOperator(
  task_id='extract_listing',
  application=extract_listing,
  conn_id='spark_default', 
  conf={'spark.master': 'spark://spark-master:7077'},
  dag=dag
)

spark_transform_listing_task = SparkSubmitOperator(
  task_id='transform_listing',
  application=transform_listing,
  conn_id='spark_default', 
  conf={'spark.master': 'spark://spark-master:7077'},
  dag=dag
)

clean_task = PythonOperator(
    task_id="clean_json_data",
    python_callable=clean_facebook_listings,
    dag=dag
)

load_task = PythonOperator(
    task_id="load_json_data",
    python_callable=load_to_snowflake,
    dag=dag
)



# End Task
end_task = DummyOperator(task_id='end', dag=dag)

start_task >> spark_extract_metadata_task >> spark_extract_listing_task >> spark_transform_listing_task >> clean_task >> load_task >> end_task