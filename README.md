ETL Process Using Airflow
This documentation outlines the process of creating an ETL (Extract, Transform, Load) pipeline using Apache Airflow to move article data from a local CSV file to a PostgreSQL data warehouse. The ETL process is scheduled to run hourly every day.

Prerequisites
1. Apache Airflow: Ensure Apache Airflow is installed and running.
2. PostgreSQL: Ensure PostgreSQL is installed and accessible.
3. CSV Data: Ensure the CSV file (articles.csv) is available on the local machine at 
   the specified path.

Setting Up the PostgreSQL Connection in Airflow
First, establish a connection to the PostgreSQL data warehouse in Airflow. 

Navigate to the Airflow web interface and set up the connection with the following details:
1. Connection ID: postgres_id
2. Connection Type: Postgres
3. Host: your_postgres_host
4. Schema: your_postgres_db
5. Login: your_postgres_user
6. Password: your_postgres_password
7. Port: your_postgres_port

![image](https://github.com/user-attachments/assets/cd4edc2d-0272-42e1-8c44-ac155d958dbe)

Creating the ETL DAG
The ETL process consists of three main tasks: extract, transform, and load. Below is the DAG (Directed Acyclic Graph) definition for the ETL process using Airflow.

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
    
Explanation
1. Extract Task: Reads the CSV file from the local file system and saves the 
   extracted data to a new CSV file.
2. Transform Task: Performs any necessary data transformations, such as 
   converting the publish date to a datetime format, and saves the transformed 
   data to another CSV file.
3. Load Task: Loads the transformed data into a PostgreSQL database.
   Execution

Once the ETL pipeline is set up, it will run each hour, transferring the data from the local CSV file to PostgreSQL and ensuring the data is up-to-date.

Verification
After the ETL process is complete, verify the data in PostgreSQL to ensure that it has been correctly transferred and transformed.

![image](https://github.com/user-attachments/assets/602e6ad1-2c44-4025-9417-755995198d42)


By following this ETL process, the articles data is efficiently moved from a local CSV file to PostgreSQL, with transformations applied as needed. The hourly schedule ensures the data remains current.
