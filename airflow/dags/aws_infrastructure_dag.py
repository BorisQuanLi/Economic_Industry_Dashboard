"""
AWS Infrastructure Management DAG for JPMC ECS Deployment

This DAG demonstrates enterprise cost-saving by:
1. Creating AWS resources on-demand
2. Running ETL pipeline on ECS
3. Destroying resources after completion
"""

from datetime import datetime, timedelta
from airflow import DAG
from airflow.providers.amazon.aws.operators.ecs import EcsRunTaskOperator
from airflow.providers.amazon.aws.operators.rds import RdsCreateDbInstanceOperator, RdsDeleteDbInstanceOperator
from airflow.providers.amazon.aws.operators.s3 import S3CreateBucketOperator, S3DeleteBucketOperator
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'jpmc-data-engineer',
    'depends_on_past': False,
    'start_date': datetime(2025, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'aws_ecs_infrastructure_pipeline',
    default_args=default_args,
    description='JPMC ECS Infrastructure with Cost Optimization',
    schedule_interval='@daily',
    catchup=False,
    tags=['jpmc', 'ecs', 'cost-optimization']
)

# 1. Create AWS RDS Instance
create_rds = RdsCreateDbInstanceOperator(
    task_id='create_rds_instance',
    db_instance_identifier='jpmc-sp500-db',
    db_instance_class='db.t3.micro',
    engine='postgres',
    master_username='postgres',
    master_user_password='{{ var.value.db_password }}',
    allocated_storage=20,
    aws_conn_id='aws_default',
    dag=dag
)

# 2. Create S3 Bucket for Data Lake
create_s3_bucket = S3CreateBucketOperator(
    task_id='create_s3_bucket',
    bucket_name='jpmc-sp500-data-lake-{{ ds_nodash }}',
    aws_conn_id='aws_default',
    dag=dag
)

# 3. Run ETL Pipeline on ECS
run_etl_ecs = EcsRunTaskOperator(
    task_id='run_etl_on_ecs',
    cluster='jpmc-ecs-cluster',
    task_definition='sp500-etl-task',
    launch_type='FARGATE',
    network_configuration={
        'awsvpcConfiguration': {
            'subnets': ['{{ var.value.subnet_id }}'],
            'securityGroups': ['{{ var.value.security_group_id }}'],
            'assignPublicIp': 'ENABLED'
        }
    },
    overrides={
        'containerOverrides': [
            {
                'name': 'etl-container',
                'environment': [
                    {'name': 'DATABASE_URL', 'value': 'postgresql://postgres:{{ var.value.db_password }}@{{ ti.xcom_pull(task_ids="create_rds_instance")["endpoint"] }}:5432/sp500_db'},
                    {'name': 'S3_BUCKET', 'value': 'jpmc-sp500-data-lake-{{ ds_nodash }}'}
                ]
            }
        ]
    },
    aws_conn_id='aws_default',
    dag=dag
)

# 4. Run FastAPI Backend on ECS
run_fastapi_ecs = EcsRunTaskOperator(
    task_id='run_fastapi_on_ecs',
    cluster='jpmc-ecs-cluster',
    task_definition='sp500-fastapi-task',
    launch_type='FARGATE',
    network_configuration={
        'awsvpcConfiguration': {
            'subnets': ['{{ var.value.subnet_id }}'],
            'securityGroups': ['{{ var.value.security_group_id }}'],
            'assignPublicIp': 'ENABLED'
        }
    },
    aws_conn_id='aws_default',
    dag=dag
)

# 5. Cleanup: Delete RDS Instance (Cost Savings)
cleanup_rds = RdsDeleteDbInstanceOperator(
    task_id='cleanup_rds_instance',
    db_instance_identifier='jpmc-sp500-db',
    skip_final_snapshot=True,
    aws_conn_id='aws_default',
    dag=dag
)

# 6. Cleanup: Delete S3 Bucket
cleanup_s3 = S3DeleteBucketOperator(
    task_id='cleanup_s3_bucket',
    bucket_name='jpmc-sp500-data-lake-{{ ds_nodash }}',
    force_delete=True,
    aws_conn_id='aws_default',
    dag=dag
)

# Define task dependencies
create_rds >> create_s3_bucket >> [run_etl_ecs, run_fastapi_ecs] >> cleanup_rds >> cleanup_s3