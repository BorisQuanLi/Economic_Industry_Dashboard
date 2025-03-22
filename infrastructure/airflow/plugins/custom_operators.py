"""
Custom operators for Airflow DAGs.
"""
from typing import Any, Callable, Dict, Optional
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

class EconomicDataOperator(BaseOperator):
    """
    Custom operator for economic data processing.
    
    This operator provides a template for handling economic data extraction,
    transformation, and loading with custom logic.
    """
    
    @apply_defaults
    def __init__(
        self,
        data_source: str,
        data_processor: Optional[Callable] = None,
        data_sink: Optional[str] = None,
        config: Optional[Dict[str, Any]] = None,
        *args, **kwargs
    ):
        """
        Initialize the operator.
        
        Args:
            data_source (str): Source of the economic data
            data_processor (Callable): Function to process the data
            data_sink (str): Destination for processed data
            config (Dict[str, Any]): Configuration parameters
        """
        super().__init__(*args, **kwargs)
        self.data_source = data_source
        self.data_processor = data_processor
        self.data_sink = data_sink
        self.config = config or {}
    
    def execute(self, context):
        """
        Execute the operator.
        
        Args:
            context: Airflow execution context
        
        Returns:
            Any: Result of processing
        """
        self.log.info(f"Processing economic data from {self.data_source}")
        
        # Fetch data from source
        # This is a placeholder - implement actual data fetching logic
        raw_data = self._fetch_data()
        
        # Process data if processor is provided
        if self.data_processor:
            processed_data = self.data_processor(raw_data)
        else:
            processed_data = raw_data
        
        # Save to sink if provided
        if self.data_sink:
            self._save_data(processed_data)
        
        return processed_data
    
    def _fetch_data(self):
        """Fetch data from source."""
        # Placeholder for data fetching logic
        self.log.info(f"Fetching data from {self.data_source}")
        return []
    
    def _save_data(self, data):
        """Save data to sink."""
        # Placeholder for data saving logic
        self.log.info(f"Saving data to {self.data_sink}")
        return True

class DataQualityOperator(BaseOperator):
    """
    Custom operator for data quality checks.
    
    This operator runs quality checks on data and can fail the task
    if quality issues are detected.
    """
    
    @apply_defaults
    def __init__(
        self,
        data_source: str,
        quality_checks: List[Callable],
        fail_on_error: bool = True,
        *args, **kwargs
    ):
        """
        Initialize the operator.
        
        Args:
            data_source (str): Source of the data to check
            quality_checks (List[Callable]): List of quality check functions
            fail_on_error (bool): Whether to fail the task if quality issues are found
        """
        super().__init__(*args, **kwargs)
        self.data_source = data_source
        self.quality_checks = quality_checks
        self.fail_on_error = fail_on_error
    
    def execute(self, context):
        """
        Execute the operator.
        
        Args:
            context: Airflow execution context
        
        Returns:
            Dict[str, Any]: Results of quality checks
        """
        self.log.info(f"Running quality checks on {self.data_source}")
        
        # Fetch data
        data = self._fetch_data()
        
        # Run quality checks
        results = {}
        has_errors = False
        
        for check_func in self.quality_checks:
            check_name = check_func.__name__
            try:
                result = check_func(data)
                results[check_name] = result
                
                if not result.get("is_valid", False):
                    has_errors = True
                    self.log.warning(f"Quality check '{check_name}' failed")
            except Exception as e:
                has_errors = True
                results[check_name] = {"error": str(e), "is_valid": False}
                self.log.error(f"Error in quality check '{check_name}': {str(e)}")
        
        # Fail task if errors and configured to do so
        if has_errors and self.fail_on_error:
            raise ValueError(f"Data quality checks failed for {self.data_source}")
        
        return results
    
    def _fetch_data(self):
        """Fetch data from source."""
        # Placeholder for data fetching logic
        self.log.info(f"Fetching data from {self.data_source}")
        return []
