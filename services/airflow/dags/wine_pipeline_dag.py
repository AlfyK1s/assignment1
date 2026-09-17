import os
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.bash import BashOperator

# Получаем абсолютный путь к корню репозитория
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
PROJECT_DIR = os.getenv("PROJECT_DIR", BASE_DIR)

default_args = {
    "owner": "airflow",
    "retries": 1,
    "retry_delay": timedelta(minutes=1),
}

with DAG(
    dag_id="wine_quality_pipeline",
    default_args=default_args,
    start_date=datetime(2026, 1, 1),
    schedule="*/5 * * * *",
    catchup=False,
    is_paused_upon_creation=False,
) as dag:

    # Активируем venv и запускаем DVC
    run_dvc_pipeline = BashOperator(
        task_id="dvc_pipeline",
        bash_command=f'cd "{PROJECT_DIR}" && source .venv/bin/activate && dvc repro',
    )

    # Деплой контейнеров Docker
    deploy_services = BashOperator(
        task_id="docker_deploy",
        bash_command=f'cd "{PROJECT_DIR}/code/deployment" && docker compose down && docker compose up -d --build',
    )

    run_dvc_pipeline >> deploy_services
