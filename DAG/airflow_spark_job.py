from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.google.cloud.operators.dataproc import (
    DataprocCreateClusterOperator,
    DataprocSubmitPySparkJobOperator,
    DataprocDeleteClusterOperator
)
from airflow.utils.dates import days_ago

default_args = {
    'owner' : 'airflow',
    'depends_on_past' : True,
    'email_on_failure' : False,
    'email_on_retry' : False,
    'retries' : 1,
    'retry_delay' : timedelta(minutes=5)
}

dag = DAG(
    'gcp_dataproc_spark_job',
    default_args = default_args,
    description = "A DAG to run Spark job on Dataproc",
    schedule_interval = timedelta(days=1),
    start_date = days_ago(1),
    catchup = False,
    tags = ['dev']
)

# Define cluster config
CLUSTER_NAME = 'spark-airflow-demo'
PROJECT_ID = "sample-443206"
REGION = 'us-central1'

CLUSTER_CONFIG = {
    "master_config": {
        "num_instances": 1, # Master Node
        "machine_type_uri": "n1-standard-2", # Machine Type
        "disk_config": {
            "boot_disk_type": "pd-standard",
             "boot_disk_size_gb": 30
             },
    },
    "worker_config": {
        "num_instances": 2, # Worker nodes
        "machine_type_uri": "n1-standard-2",
        "disk_config": {
            "boot_disk_type": "pd-standard", 
            "boot_disk_size_gb": 30},
    },
    'software_config':{
        'image_version' : '2.2.26-debian12'  # Image version
    }
}

create_cluster = DataprocCreateClusterOperator(
    task_id = 'create_cluster',
    cluster_name = CLUSTER_NAME,
    project_id = PROJECT_ID,
    region = REGION,
    cluster_config = CLUSTER_CONFIG,
    dag = dag
)

pyspark_job = {
    'main_python_file_uri': 'gs://airflow_projects_repo/airflow-project-1/spark-code/employee_batch_job.py'
}

# spark_job_resources_param = {
#     'spark.executor.instances' : '4',
#     'spark.executor.memory' : '4g',
#     'spark.executor.cores' : '2',
#     'spark.driver.memory' : '2g',
#     'spark.driver.cores' : '2'
# }

submit_pyspark_job = DataprocSubmitPySparkJobOperator(
    task_id = 'submit_pyspark_job',
    main = pyspark_job['main_python_file_uri'],
    cluster_name = CLUSTER_NAME,
    project_id = PROJECT_ID,
    region = REGION,
    # dataproc_pyspark_properties = spark_job_resources_param,
    dag = dag
)

delete_cluster = DataprocDeleteClusterOperator(
    task_id = 'delete_cluster',
    cluster_name = CLUSTER_NAME,
    project_id = PROJECT_ID,
    region = REGION,
    trigger_rule = "all_done", # ensures cluster deletion if spark job fails 
    dag = dag,
)

create_cluster >> submit_pyspark_job >> delete_cluster