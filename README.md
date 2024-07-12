ETL Pipeline Documentation for Articles Data Using Airflow
Overview
This documentation outlines the creation and configuration of an ETL (Extract, Transform, Load) pipeline using Airflow to transfer article data from a CSV file on a local laptop to a PostgreSQL data warehouse. The ETL process is scheduled to run every hour.

Prerequisites
Before setting up the ETL pipeline, ensure that Airflow is properly installed and configured. Additionally, establish a connection to the PostgreSQL database.

Airflow Connection to PostgreSQL
Access the Airflow UI.
Navigate to Admin > Connections.
Create a new connection with the following details:
Conn Id: postgres_id
Conn Type: Postgres
Host: your_postgresql_host
Schema: your_database_name
Login: your_username
Password: your_password
Port: 5432 (default port for PostgreSQL)


ETL Pipeline Implementation
ETL DAG Definition
Create an Airflow DAG for the ETL process using the following code:

python
Salin kode
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
    schedule_interval='@hourly',  # Schedule to run each hour
    catchup=False  # Disabling catchup prevents backfilling for this DAG
) as dag:

    extract_task = extract()
    transform_task = transform(extract_task)
    load_task = load(transform_task)

    extract_task >> transform_task >> load_task
Explanation of the ETL Process
Extract: Reads the article data from a CSV file located at /opt/airflow/dags/weekly_6/dataset/articles.csv and saves the extracted data to articles_extracted_2.csv.

Transform: Converts the publish_date column to datetime format and saves the transformed data to articles_transformed_2.csv.

Load: Loads the transformed data into the articles_load table in the PostgreSQL database using the connection specified by postgres_id.

Monitoring and Verification
After the ETL process is set up and running, you can monitor the status of the tasks in the Airflow UI. Verify that the data has been successfully loaded into the PostgreSQL database by querying the articles_load table.



This completes the setup of the ETL pipeline using Airflow.
