from datetime import timedelta

from airflow.models import DAG
from airflow.operators.dummy_operator import DummyOperator 
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

#----------------- DAG -----------------#

dag = DAG(
  dag_id="Facebook_Data_Collect_DAG",
  schedule_interval=None,
  start_date=days_ago(0),
  catchup=False,
  dagrun_timeout=timedelta(minutes=360),
  max_active_runs=4
)

start_task = DummyOperator(task_id='start', dag=dag)

end_task = DummyOperator(task_id='end', dag=dag)

start_task >> end_task