import os
from typing import Dict

from airflow.decorators import dag, task
from airflow.exceptions import AirflowException
from airflow.models.param import Param
from airflow.operators.python import get_current_context
from airflow.providers.cncf.kubernetes.operators.kubernetes_pod import (
    KubernetesPodOperator,
)
from airflow.utils.dates import datetime, timedelta

# Documentation
doc_md_dag = """
DAG for processing drug mentions in publications and clinical trials.

The pipeline processes data from multiple sources:
- drugs.csv: List of drugs with their names and IDs
- pubmed.csv/json: PubMed article data
- clinical_trials.csv: Clinical trials data

Generates a graph showing relationships between drugs, publications, and journals.

Variables Used:
- env: Environment (dev/prod)
- kubernetes_config: K8s configuration parameters
- container_config: Docker container configuration

v1.0.0 (2024-10-25): Initial version
"""

# Parameters
PROJECT_ENV = os.getenv("env", "dev")
TEAM = "SERVIER"
APP_NAME = "drug-graph"
DAG_ID = "servier_drug_graph"
DAG_DESC = "Process drug mentions in publications and clinical trials"

# Kubernetes Configuration
K8S_CONFIG = {
    "namespace": "drug-graph",
    "service_account": "default",
    "connection_id": "kubernetes_default",
    "config_file": "/home/airflow/composer_kube_config",
    "container_image": "drug-graph-app:latest",
}

MAX_ACTIVE_TASKS = 10
MAX_ACTIVE_RUNS = 1

DEFAULT_ARGS = {
    "owner": TEAM,
    "depends_on_past": False,
    "start_date": datetime(2024, 1, 1),
    "email": ["mehdigati@hotmail.com"],
    "email_on_failure": True,
    "email_on_retry": False,
    "retries": 1,
    "retry_delay": timedelta(minutes=5),
}

DEFAULT_PARAMS = {
    "APP_NAME": Param(
        default=APP_NAME,
        type="string",
        description="Application name",
    ),
    "IMAGE_VERSION": Param(
        default="latest",
        type="string",
        description="Docker image version",
    ),
}


def log(func):
    """Decorator for logging function execution"""

    def wrapper(*args, **kwargs):
        print(f"[{APP_NAME}] Executing {func.__name__}...")
        result = func(*args, **kwargs)
        print(f"[{APP_NAME}] {func.__name__} executed successfully.")
        return result

    return wrapper


def handle_errors(func):
    """Decorator for error handling"""

    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except Exception as e:
            raise AirflowException(f"[{APP_NAME}] Error in {func.__name__}: {str(e)}")

    return wrapper


@log
@handle_errors
def get_kubernetes_config() -> Dict:
    """Get Kubernetes configuration with environment-specific settings"""
    return {
        "namespace": K8S_CONFIG["namespace"],
        "service_account_name": K8S_CONFIG["service_account"],
        "kubernetes_conn_id": K8S_CONFIG["connection_id"],
        "config_file": K8S_CONFIG["config_file"],
        "image": K8S_CONFIG["container_image"],
        "startup_timeout_seconds": 600,
        "is_delete_operator_pod": True,
        "image_pull_policy": "Always",
        "get_logs": True,
    }


def create_dag():
    @dag(
        dag_id=DAG_ID,
        schedule=None,
        start_date=DEFAULT_ARGS["start_date"],
        default_args=DEFAULT_ARGS,
        params=DEFAULT_PARAMS,
        doc_md=doc_md_dag,
        catchup=False,
        max_active_tasks=MAX_ACTIVE_TASKS,
        max_active_runs=MAX_ACTIVE_RUNS,
        tags=[TEAM],
    )
    def servier_drug_graph():
        @task()
        def process_drug_mentions():
            """Task to process drug mentions data using KubernetesPodOperator"""
            k8s_config = get_kubernetes_config()

            return KubernetesPodOperator(
                task_id="process_drug_mentions",
                name="drug-graph-process",
                cmds=["poetry", "run", "python"],
                arguments=["app/main.py", "generate_graph"],
                **k8s_config,
            ).execute(get_current_context())

        @task()
        def get_journal_with_most_drugs():
            """Task to analyze journals with most drug mentions"""
            k8s_config = get_kubernetes_config()

            return KubernetesPodOperator(
                task_id="get_journal_with_most_drugs",
                name="drug-graph-analysis",
                cmds=["poetry", "run", "python"],
                arguments=["app/main.py", "get_journal_with_most_drugs"],
                **k8s_config,
            ).execute(get_current_context())

        process_drug_mentions() >> get_journal_with_most_drugs()

    return servier_drug_graph()


create_dag()
