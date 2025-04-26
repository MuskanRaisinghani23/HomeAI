from datetime import timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy_operator import DummyOperator 
from airflow.utils.dates import days_ago
import os

from scripts.email.sendemail import send_email


dag = DAG(
  dag_id="send_email",
  schedule_interval=None,
  start_date=days_ago(0),
  catchup=False,
  dagrun_timeout=timedelta(minutes=360),
  max_active_runs=4
)

# Start Task
start_task = DummyOperator(task_id='start', dag=dag)

send_task = PythonOperator(
  task_id="send_email_notification",
  python_callable=send_email,
  dag=dag
)


# End Task
end_task = DummyOperator(task_id='end', dag=dag)

start_task >> send_task >> end_task
 