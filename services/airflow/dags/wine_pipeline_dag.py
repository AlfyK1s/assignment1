import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

PROJECT_DIR = os.getenv("PROJECT_DIR", "/opt/airflow/project")

default_args = {
    "owner": "airflow",
    "depends_on_past": False,
    "start_date": datetime(2026, 1, 1),
    "email_on_failure": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    "wine_quality_pipeline",
    default_args=default_args,
    description="End-to-end wine classification pipeline every 5 mins",
    schedule_interval="*/5 * * * *",
    catchup=False,
) as dag:

    stage_1_data = BashOperator(
        task_id="data_engineering",
        bash_command=f"cd {PROJECT_DIR} && python code/datasets/process_data.py",
    )

    stage_2_model = BashOperator(
        task_id="model_engineering",
        bash_command=f"cd {PROJECT_DIR} && python code/models/train.py",
    )

    stage_3_deploy = BashOperator(
        task_id="deployment",
        bash_command=f"cd {PROJECT_DIR}/code/deployment && docker compose down && docker compose up -d --build",
    )

    stage_1_data >> stage_2_model >> stage_3_deploy