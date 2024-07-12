from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime, timedelta
import logging

def check_postgres_connection():
    try:
        # Initialize the PostgresHook
        pg_hook = PostgresHook(postgres_conn_id='postgres_default')
        
        # Try to get a connection
        connection = pg_hook.get_conn()
        
        # If connection is successful
        logging.info("Connection to PostgreSQL is successful!")
        
    except Exception as e:
        logging.error(f"Error connecting to PostgreSQL: {e}")

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 7, 9),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

with DAG('check_postgres_connection',
        default_args=default_args,
        schedule_interval='@once',
        catchup=False) as dag:

    check_connection_task = PythonOperator(
        task_id='check_postgres_connection',
        python_callable=check_postgres_connection,
    )

    check_connection_task 
