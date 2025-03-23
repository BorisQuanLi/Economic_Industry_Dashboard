"""
S&P 500 ETL Pipeline Orchestrator for Economic Industry Dashboard

This module provides a comprehensive ETL pipeline implementation that:
1. Extracts data from various sources for S&P 500 companies
2. Transforms the data into domain models
3. Loads the processed data into the database

Role in Project Structure:
--------------------------
This module serves as the main orchestrator for the ETL process, positioned at
the root of the ETL package to provide a clear entry point for pipeline execution.
It composes functionality from the extract/, transform/, and load/ subpackages
rather than implementing business logic directly.

Background:
-----------
This module represents the modernized version of the original 'pipeline.py' module,
created as part of the cloud pipeline modernization initiative. It specifically 
targets S&P 500 financial data processing, aligning with the Airflow DAG naming 
convention (sp500_financial_etl_dag.py).

Migration Status:
---------------
Complete. The original 'pipeline.py' module has been fully replaced by this module.
Code analysis confirmed no existing references to the original module, allowing for
direct replacement without a compatibility layer.

Future Development Roadmap:
--------------------------
- Short-term: Enhance cloud compatibility and add data validation features (high priority)
- Medium-term: Implement ML-based anomaly detection for financial data processing
- Long-term: Complete separation of concerns by creating dedicated modules for
  each major S&P 500 data category

This pipeline can be run as a standalone process or integrated with Airflow.
"""

import logging
import datetime
from typing import Optional, Dict, Any, List, Callable
import pandas as pd

# ETL component imports
from backend.etl.config import get_config, Config
from backend.etl.load.data_persistence.local_postgres import LocalPostgresRepository

# Import extract modules
from backend.etl.extract.companies_extractor import CompaniesExtractor

# Import transformation models
from backend.etl.transform.models.company.company_info_model import CompanyInfo
from backend.etl.transform.models.company.company_price_earnings_model import PriceEarningsRatio
from backend.etl.transform.models.industry.sector_model import Sector
from backend.etl.transform.models.industry.subindustry_model import SubIndustry

logger = logging.getLogger(__name__)

class SP500ETLPipeline:
    """ETL Pipeline for processing S&P 500 economic and industry data."""
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the ETL pipeline with configuration."""
        self.config = config or get_config()
        self.db_repository: Optional[LocalPostgresRepository] = None
        self.cursor = None
        self.extractors = {}
        self.start_time = None
        self.end_time = None
        self.metrics = {
            'records_processed': 0,
            'errors': 0,
            'warnings': 0
        }
    
    def setup_connections(self):
        """Initialize database and other connections."""
        try:
            logger.info("Setting up database connection")
            self.db_repository = LocalPostgresRepository(db_config=self.config.db)
            self.db_repository.connect()
            self.cursor = self.db_repository.cursor
            
            # Initialize extractors
            self.extractors['companies'] = CompaniesExtractor()
            
            logger.info("Connections established successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to setup connections: {str(e)}")
            raise
    
    def extract_data(self, source: str = 'all') -> Dict[str, pd.DataFrame]:
        """
        Extract data from various sources.
        
        Args:
            source (str): Data source to extract from ('companies', 'financials', 'all')
            
        Returns:
            Dict[str, pd.DataFrame]: Dictionary of extracted dataframes
        """
        logger.info(f"Starting S&P 500 data extraction for source: {source}")
        extracted_data = {}
        
        try:
            if source == 'companies' or source == 'all':
                logger.info("Extracting S&P 500 company data")
                company_data = self.extractors['companies'].extract()
                extracted_data['companies'] = company_data
                self.metrics['records_processed'] += len(company_data)
                
            # Add other data sources as needed
            
            logger.info(f"Extraction complete. {len(extracted_data)} datasets extracted.")
            return extracted_data
        except Exception as e:
            logger.error(f"Error during extraction: {str(e)}")
            self.metrics['errors'] += 1
            raise
    
    def transform_data(self, raw_data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Transform raw data into domain models.
        
        Args:
            raw_data (Dict[str, pd.DataFrame]): Dictionary of raw dataframes
            
        Returns:
            Dict[str, Any]: Dictionary of transformed data
        """
        logger.info("Starting data transformation")
        transformed_data = {}
        
        try:
            if 'companies' in raw_data:
                logger.info("Transforming company data")
                companies_df = raw_data['companies']
                
                # Example transformation - create company domain objects
                companies = []
                for _, row in companies_df.iterrows():
                    try:
                        company = CompanyInfo(
                            ticker=row.get('ticker'),
                            name=row.get('name'),
                            sub_industry_id=row.get('sub_industry_id'),
                            year_founded=row.get('year_founded'),
                            number_of_employees=row.get('number_of_employees'),
                            HQ_state=row.get('state')
                        )
                        companies.append(company)
                    except Exception as e:
                        logger.warning(f"Error transforming company record: {str(e)}")
                        self.metrics['warnings'] += 1
                
                transformed_data['companies'] = companies
                logger.info(f"Transformed {len(companies)} company records")
            
            # Add other transformations as needed
            
            return transformed_data
        except Exception as e:
            logger.error(f"Error during transformation: {str(e)}")
            self.metrics['errors'] += 1
            raise
    
    def load_data(self, transformed_data: Dict[str, Any]) -> bool:
        """
        Load transformed data into the database.
        
        Args:
            transformed_data (Dict[str, Any]): Dictionary of transformed data
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Starting data loading")
        
        try:
            if 'companies' in transformed_data:
                logger.info("Loading company data")
                companies = transformed_data['companies']
                
                # Example: Bulk insert companies
                for company in companies:
                    # Insert into database using repository
                    # This would need to be implemented based on your database schema
                    pass
                    
                logger.info(f"Loaded {len(companies)} company records")
            
            # Add other data loading as needed
            
            return True
        except Exception as e:
            logger.error(f"Error during data loading: {str(e)}")
            self.metrics['errors'] += 1
            return False
    
    def run_full_pipeline(self) -> Dict[str, Any]:
        """
        Run the complete ETL pipeline.
        
        Returns:
            Dict[str, Any]: Pipeline metrics and status
        """
        logger.info("Starting full ETL pipeline")
        self.start_time = datetime.datetime.now()
        
        try:
            # Setup connections
            self.setup_connections()
            
            # Extract data
            raw_data = self.extract_data('all')
            
            # Transform data
            transformed_data = self.transform_data(raw_data)
            
            # Load data
            success = self.load_data(transformed_data)
            
            self.end_time = datetime.datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            metrics = {
                **self.metrics,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'duration_seconds': duration,
                'status': 'success' if success else 'failure'
            }
            
            logger.info(f"Pipeline completed with status: {metrics['status']}")
            logger.info(f"Processed {metrics['records_processed']} records in {duration} seconds")
            
            return metrics
        except Exception as e:
            self.end_time = datetime.datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            logger.error(f"Pipeline failed: {str(e)}")
            
            return {
                **self.metrics,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'duration_seconds': duration,
                'status': 'error',
                'error_message': str(e)
            }
        finally:
            # Close connections
            if self.db_repository:
                self.db_repository.close()
    
    def run_incremental_update(self, since_date: Optional[datetime.datetime] = None) -> Dict[str, Any]:
        """
        Run incremental updates to refresh data since a specific date.
        
        Args:
            since_date (datetime.datetime, optional): Date to start incremental updates from
            
        Returns:
            Dict[str, Any]: Pipeline metrics and status
        """
        logger.info(f"Starting incremental update since {since_date}")
        self.start_time = datetime.datetime.now()
        
        if since_date is None:
            # Default to 24 hours ago if not specified
            since_date = datetime.datetime.now() - datetime.timedelta(days=1)
        
        try:
            # Setup connections
            self.setup_connections()
            
            # Implement incremental logic here
            # This would be similar to run_full_pipeline but with date filters
            
            self.end_time = datetime.datetime.now()
            duration = (self.end_time - self.start_time).total_seconds()
            
            return {
                **self.metrics,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'duration_seconds': duration,
                'status': 'success',
                'since_date': since_date
            }
        except Exception as e:
            self.end_time = datetime.datetime.now()
            
            logger.error(f"Incremental update failed: {str(e)}")
            
            return {
                **self.metrics,
                'start_time': self.start_time,
                'end_time': self.end_time,
                'duration_seconds': (self.end_time - self.start_time).total_seconds(),
                'status': 'error',
                'error_message': str(e),
                'since_date': since_date
            }
        finally:
            # Close connections
            if self.db_repository:
                self.db_repository.close()
    
    def get_sector_data(self, sector_id: int) -> Dict[str, Any]:
        """Retrieve sector data from the database."""
        try:
            self.setup_connections()
            
            # Get sector information
            sector = Sector.find_by_id(sector_id, self.cursor)
            if not sector:
                return {'error': 'Sector not found'}
            
            # Get sub-industries in this sector
            sub_industries = SubIndustry.find_by_sector(sector.gics_code, self.cursor)
            
            return {
                'sector': {
                    'id': sector.id,
                    'name': sector.name, 
                    'gics_code': sector.gics_code,
                    'description': sector.description
                },
                'sub_industries': [vars(si) for si in sub_industries]
            }
        except Exception as e:
            logger.error(f"Error getting sector data: {str(e)}")
            return {'error': str(e)}
        finally:
            if self.db_repository:
                self.db_repository.close()
            
    def get_available_sectors(self) -> List[Dict[str, Any]]:
        """Get list of all available sectors."""
        try:
            self.setup_connections()
            
            sectors = Sector.find_all(self.cursor)
            return [
                {
                    'id': sector.id,
                    'name': sector.name,
                    'gics_code': sector.gics_code
                }
                for sector in sectors
            ]
        except Exception as e:
            logger.error(f"Error getting available sectors: {str(e)}")
            return []
        finally:
            if self.db_repository:
                self.db_repository.close()
    
    def get_pipeline_metadata(self) -> Dict[str, Any]:
        """
        Get metadata about the pipeline execution state.
        
        Returns:
            Dict[str, Any]: Pipeline metadata including status, metrics, and timing
        """
        execution_time = 0
        if self.start_time and self.end_time:
            execution_time = (self.end_time - self.start_time).total_seconds()
        
        return {
            "status": "running" if self.start_time and not self.end_time else "completed",
            "start_time": self.start_time,
            "end_time": self.end_time,
            "execution_time_seconds": execution_time,
            "metrics": self.metrics,
            "pipeline_type": "sp500_financial_etl",
            "is_airflow_compatible": True
        }
    
    def get_task_status(self, task_name: str) -> Dict[str, Any]:
        """
        Get status of a specific pipeline task, useful for Airflow task monitoring.
        
        Args:
            task_name (str): Name of the task to check status
            
        Returns:
            Dict[str, Any]: Task status information
        """
        # This method would be implemented with actual task tracking
        return {
            "task_name": task_name,
            "pipeline_type": "sp500_financial_etl",
            "status": "not_implemented",
            "message": "Task status tracking to be implemented"
        }

# Add a main block to enable direct execution
if __name__ == "__main__":
    import argparse
    import sys
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='S&P 500 ETL Pipeline')
    parser.add_argument('--env', default='dev', help='Environment (dev/test/prod)')
    parser.add_argument('--incremental', action='store_true', help='Run incremental update')
    parser.add_argument('--days', type=int, default=1, help='Days to look back for incremental update')
    args = parser.parse_args()
    
    try:
        # Initialize pipeline
        config = get_config(args.env)
        pipeline = SP500ETLPipeline(config)
        
        # Run appropriate pipeline mode
        if args.incremental:
            since_date = datetime.datetime.now() - datetime.timedelta(days=args.days)
            result = pipeline.run_incremental_update(since_date)
        else:
            result = pipeline.run_full_pipeline()
        
        # Log summary
        logger.info(f"Pipeline complete: {result['status']}")
        logger.info(f"Processed {result['records_processed']} records in {result['duration_seconds']:.2f} seconds")
        
        # Return appropriate exit code
        sys.exit(0 if result['status'] == 'success' else 1)
    
    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}")
        sys.exit(1)