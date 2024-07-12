from airflow import DAG
from airflow.exceptions import AirflowException
from airflow.decorators import task
from airflow.providers.postgres.hooks.postgres import PostgresHook
from datetime import datetime, timedelta
import pandas as pd
import logging

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2024, 7, 9),
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

@task()
def extract():
    source_path = "/opt/airflow/dags/weekly_6/dataset/articles.csv"
    try:
        df = pd.read_csv(source_path)
        extracted_file_path = '/opt/airflow/dags/weekly_6/dataset/articles_extracted_2.csv'
        df.to_csv(extracted_file_path, index=False)
        return extracted_file_path
    except Exception as e:
        logging.error(f"Error extracting data: {e}")
        raise AirflowException(f"Failed to extract data: {e}")

@task()
def transform(extracted_file_path: str):
    try:
        df = pd.read_csv(extracted_file_path)
        # Perform data transformation if needed
        df['publish_date'] = pd.to_datetime(df['publish_date'])
        transformed_file_path = '/opt/airflow/dags/weekly_6/dataset/articles_transformed_2.csv'
        df.to_csv(transformed_file_path, index=False)
        return transformed_file_path
    except Exception as e:
        logging.error(f"Error transforming data: {e}")
        raise AirflowException(f"Failed to transform data: {e}")

@task()
def load(transformed_file_path: str):
    try:
        df = pd.read_csv(transformed_file_path)
        pg_hook = PostgresHook(postgres_conn_id='postgres_id')
        engine = pg_hook.get_sqlalchemy_engine()
        df.to_sql('articles_load', engine, if_exists='replace', index=False)
        logging.info("Data successfully loaded into PostgreSQL.")
    except Exception as e:
        logging.error(f"Error loading data into PostgreSQL: {e}")
        raise AirflowException(f"Failed to load data into PostgreSQL: {e}")

with DAG(
    dag_id="etl_articles_csv_postgres_kumparan",
    default_args=default_args,
    schedule_interval=None,  # Set to None to disable automatic scheduling
    catchup=False  # Disabling catchup prevents backfilling for this DAG
) as dag:

    extract_task = extract()
    transform_task = transform(extract_task)
    load_task = load(transform_task)

    extract_task >> transform_task >> load_task

