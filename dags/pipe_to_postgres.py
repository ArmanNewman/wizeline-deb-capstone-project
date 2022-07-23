import os
import datetime
import psycopg2
from airflow import DAG
from airflow.providers.postgres.hooks.postgres import PostgresHook
from airflow.providers.postgres.operators.postgres import PostgresOperator

conn = psycopg2.connect(
    database='debdb',
    user='airflow_user',
    password=os.getenv("POSTGRES_PASS")
)

cur = conn.cursor()

p_hook = PostgresHook({'cursor': cur})

default_args = {
    "owner": "airflow",
    "start_date": datetime.datetime(2022, 7, 18),
    "end_date": datetime.datetime(2022, 12, 31),
    "depends_on_past": False,
    #'email': ['airflow@example.com'],
    #'email_on_failure': False,
    # 'email_on_retry': False,
    # If a task fails, retry it once after waiting
    # at least 15 minutes
    "retries": 0,
    # "retry_delay": datetime.timedelta(minutes=15),
}

dag_psql = DAG(
    dag_id="populate_postgres",
    default_args=default_args,
    # schedule_interval='0 0 * * *',
    schedule_interval="@once",
    catchup=False,
    dagrun_timeout=datetime.timedelta(minutes=60),
    description="Populates PostgreSQL table user_purchase",
    start_date=default_args["start_date"],
)

with open("/home/armando/wizeline_deb/capstone_project/dags/SQL/create_table.sql", mode='r', encoding="utf-8") as f:
    create_table_sql = f.read()

create_table = PostgresOperator(
    sql=create_table_sql,
    task_id="create_table",
    postgres_conn_id="postgres_local",
    dag=dag_psql,
    autocommit=True
)

with open("/home/armando/wizeline_deb/capstone_project/dags/SQL/upload_csv.sql", mode='r', encoding="utf-8") as f:
    populate_sql = f.read()

populate_table = PostgresOperator(
    sql=populate_sql,
    task_id="populate_table",
    postgres_conn_id="postgres_local",
    dag=dag_psql,
    autocommit=True
)

create_table >> populate_table

if __name__ == "__main__":
    dag_psql.cli()
