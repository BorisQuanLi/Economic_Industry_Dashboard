"""
Tests for S&P 500 financial ETL pipeline DAG.
"""
import unittest
from datetime import datetime
import os
import sys

# Add parent directory to Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../')))

from airflow.models import DagBag

class TestSP500FinancialETLDag(unittest.TestCase):
    """Test the S&P 500 financial ETL pipeline DAG."""
    
    def setUp(self):
        """Set up the test case."""
        self.dagbag = DagBag(dag_folder='../dags', include_examples=False)
    
    def test_dag_loaded(self):
        """Test that the DAG is loaded correctly."""
        self.assertIn('sp500_financial_etl', self.dagbag.dags)
        self.assertEqual(len(self.dagbag.import_errors), 0, f"DAG import errors: {self.dagbag.import_errors}")
    
    def test_dag_structure(self):
        """Test the structure of the DAG."""
        dag = self.dagbag.get_dag('sp500_financial_etl')
        
        # Check DAG default args
        self.assertEqual(dag.default_args['owner'], 'airflow')
        self.assertEqual(dag.default_args['retries'], 1)
        
        # Check DAG tasks
        tasks = dag.tasks
        task_ids = [task.task_id for task in tasks]
        self.assertIn('full_pipeline', task_ids)
        self.assertIn('incremental_update', task_ids)
        
        # Check dependencies
        full_pipeline_task = dag.get_task('full_pipeline')
        incremental_update_task = dag.get_task('incremental_update')
        
        upstream_task_ids = [task.task_id for task in incremental_update_task.upstream_list]
        self.assertIn('full_pipeline', upstream_task_ids)
    
    def test_task_functions(self):
        """Test the task functions."""
        dag = self.dagbag.get_dag('sp500_financial_etl')
        
        # Check that task functions exist
        full_pipeline_task = dag.get_task('full_pipeline')
        incremental_update_task = dag.get_task('incremental_update')
        
        # Check the function is callable
        self.assertTrue(callable(full_pipeline_task.python_callable))
        self.assertTrue(callable(incremental_update_task.python_callable))
        
        # Check function signature
        self.assertEqual(full_pipeline_task.python_callable.__name__, 'run_full_pipeline')
        self.assertEqual(incremental_update_task.python_callable.__name__, 'run_incremental_update')

if __name__ == '__main__':
    unittest.main()
