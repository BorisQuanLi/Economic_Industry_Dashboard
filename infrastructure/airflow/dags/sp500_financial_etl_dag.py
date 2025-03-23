"""
Airflow DAG for Economic Industry Dashboard ETL pipeline.
This DAG orchestrates the extraction, transformation, and loading of historical performance data 
of S&P 500 component stocks and company quarterly filings with the Securities and Exchange Commission (SEC).
"""
import logging
import os
import sys
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator

# Use relative path to project root - more portable
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../')))

# Import ETL pipeline
from backend.etl.load.data_persistence.base import DevelopmentConfig
from backend.etl.sp500_financial_etl_pipeline import SP500ETLPipeline

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2023, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'sp500_financial_etl',
    default_args=default_args,
    description='Pipeline for S&P 500 financial data ETL process',
    schedule_interval=timedelta(days=1),
    catchup=False,
)

# Create ETL task functions
def run_full_pipeline(**kwargs):
    """Run the complete ETL pipeline."""
    logging.info("Starting ETL pipeline")
    config = DevelopmentConfig()
    pipeline = SP500ETLPipeline(config)
    results = pipeline.run_full_pipeline()
    logging.info(f"ETL pipeline completed with status: {results['status']}")
    return results

def run_incremental_update(**kwargs):
    """Run an incremental update to the data."""
    execution_date = kwargs.get('execution_date')
    logging.info(f"Running incremental update from: {execution_date}")
    
    config = DevelopmentConfig()
    pipeline = SP500ETLPipeline(config)
    # Use execution_date as the starting point for data updates
    results = pipeline.run_incremental_update(since_date=execution_date)
    
    logging.info(f"Incremental update completed with status: {results['status']}")
    return results

# Create DAG tasks
full_pipeline_task = PythonOperator(
    task_id='full_pipeline',
    python_callable=run_full_pipeline,
    provide_context=True,
    dag=dag,
)

incremental_update_task = PythonOperator(
    task_id='incremental_update',
    python_callable=run_incremental_update,
    provide_context=True,
    dag=dag,
)

# Set task dependencies (sequential for now)
full_pipeline_task >> incremental_update_task
