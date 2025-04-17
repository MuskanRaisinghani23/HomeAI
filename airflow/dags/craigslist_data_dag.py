from datetime import timedelta
from airflow import DAG
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.python import PythonOperator
from airflow.operators.dummy_operator import DummyOperator 
from airflow.utils.dates import days_ago
import os

from scripts.craigslist.transform_listings import transform_listings
from scripts.craigslist.load_listings import load_to_snowflake

current_directory = os.path.dirname(os.path.realpath(__file__))
extract_listing = os.path.join(current_directory, 'spark', 'craigslist','extract_listing.py')


dag = DAG(
  dag_id="craigslist_scraper",
  schedule_interval=None,
  start_date=days_ago(0),
  catchup=False,
  dagrun_timeout=timedelta(minutes=360),
  max_active_runs=4
)

# Start Task
start_task = DummyOperator(task_id='start', dag=dag)

spark_extract_listing_task = SparkSubmitOperator(
  task_id='extract_listing',
  application=extract_listing,
  conn_id='spark_default', 
  conf={'spark.master': 'spark://spark-master:7077'},
  dag=dag
)


transform_task = PythonOperator(
  task_id="transfrom_data",
  python_callable=transform_listings,
  dag=dag
)

load_task = PythonOperator(
  task_id="load_data",
  python_callable=load_to_snowflake,
  dag=dag
)



# End Task
end_task = DummyOperator(task_id='end', dag=dag)

start_task >> spark_extract_listing_task >> transform_task >> load_task >> end_task
