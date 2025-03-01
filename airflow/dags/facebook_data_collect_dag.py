from datetime import timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator 
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago
from airflow.utils.task_group import TaskGroup
from facebook.extract_metadata import extract_metadata_for_city
from facebook.transform_metadata import transform_metadata_for_city
from facebook.load_metadata import load_metadata_for_city

# Function to extract data for a specific city
def extract_data_for_city(city, **kwargs):
  result_df = extract_metadata_for_city(city=city)
  kwargs['ti'].xcom_push(key=f'extract_df_metadata_{city}', value=result_df)

def transform_data_for_city(city, **kwargs):
  extracted_data = kwargs['ti'].xcom_pull(task_ids=f'city_tasks.extract_metadata_{city}', key=f'extract_df_metadata_{city}')
  transformed_data = transform_metadata_for_city(extracted_data)
  kwargs['ti'].xcom_push(key=f'transformed_df_metadata_{city}', value=transformed_data)

def load_data_for_city(city, **kwargs):
  extracted_data = kwargs['ti'].xcom_pull(task_ids=f'city_tasks.extract_metadata_{city}', key=f'transformed_df_metadata_{city}')
  load_metadata_for_city(extracted_data)

# List of cities to process (This could be dynamic from a config or a database)
cities = ["boston", "sanfrancisco", "newyork", "chicago", "losangeles", "miami"]  # Add all cities here

# Define the DAG
dag = DAG(
  dag_id="Facebook_Data_Collect_DAG",
  schedule_interval=None,
  start_date=days_ago(0),
  catchup=False,
  dagrun_timeout=timedelta(minutes=360),
  max_active_runs=4,
  default_args={
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
  },
)

# Start Task
start_task = DummyOperator(task_id='start', dag=dag)

# Create a TaskGroup to hold tasks for each city
with TaskGroup("city_tasks", dag=dag) as city_task_group:
  # Dynamically generate tasks for each city
  city_tasks = []
  for city in cities:
    # Task for extracting metadata
    extract_task = PythonOperator(
      task_id=f"extract_metadata_{city}",
      python_callable=extract_data_for_city,
      op_args=[city],
      provide_context=True,
      dag=dag,
    )
    # Task for transforming metadata
    transform_task = PythonOperator(
      task_id=f"transform_metadata_{city}",
      python_callable=transform_data_for_city,
      op_args=[city],
      provide_context=True,
      dag=dag,
    )
    # Task for load metadata
    load_task = PythonOperator(
      task_id=f"load_metadata_{city}",
      python_callable=transform_data_for_city,
      op_args=[city],
      provide_context=True,
      dag=dag,
    )
    extract_task >> transform_task >> load_task
    city_tasks.append((extract_task, transform_task))

# End Task
end_task = DummyOperator(task_id='end', dag=dag)

# Set the task dependencies
start_task >> city_task_group >> end_task
