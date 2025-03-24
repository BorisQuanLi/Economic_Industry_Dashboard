#!/usr/bin/env python
"""
Command-line interface for the S&P 500 ETL Pipeline.

This module provides a comprehensive CLI to run the S&P 500 ETL pipeline
with various options. It serves as the primary entry point for pipeline execution
from the command line.

Usage:
    python sp500_etl_cli.py --env=dev
    python sp500_etl_cli.py --incremental --days=2
    python sp500_etl_cli.py --sector=Technology
    python sp500_etl_cli.py --list-sectors
    python sp500_etl_cli.py --metadata
"""

import argparse
import logging
import sys
import datetime
from typing import Optional, Dict, Any

# Import the main pipeline implementation
from backend.etl.sp500_financial_etl_pipeline import SP500ETLPipeline
from backend.etl.config import get_config

logger = logging.getLogger(__name__)

def setup_logging(verbose: bool = False):
    """Configure logging"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

def format_result_summary(result: Dict[str, Any]) -> None:
    """Format and print a summary of pipeline execution results"""
    if not isinstance(result, dict):
        logger.info("Operation completed successfully")
        return
        
    if 'status' in result:
        logger.info(f"Pipeline complete: {result['status']}")
        
    if 'records_processed' in result and 'duration_seconds' in result:
        logger.info(f"Processed {result['records_processed']} records in {result['duration_seconds']:.2f} seconds")
        
    if 'error_message' in result:
        logger.error(f"Error: {result['error_message']}")

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description='S&P 500 ETL Pipeline')
    parser.add_argument('--env', default='dev', help='Environment (dev/test/prod)')
    parser.add_argument('--incremental', action='store_true', help='Run incremental update')
    parser.add_argument('--days', type=int, default=1, help='Days to look back for incremental update')
    parser.add_argument('--sector', help='Process a specific sector only')
    parser.add_argument('--list-sectors', action='store_true', help='List all available sectors')
    parser.add_argument('--metadata', action='store_true', help='Show pipeline metadata')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    try:
        # Initialize pipeline with proper configuration
        config = get_config(args.env)
        pipeline = SP500ETLPipeline(config)
        
        # Select operation mode
        if args.list_sectors:
            logger.info("Retrieving available sectors")
            result = pipeline.get_available_sectors()
            if result:
                logger.info("Available sectors:")
                for sector in result:
                    logger.info(f"  - {sector['name']} (ID: {sector['id']}, GICS: {sector['gics_code']})")
            else:
                logger.info("No sectors found or error retrieving sectors")
                
        elif args.metadata:
            logger.info("Retrieving pipeline metadata")
            result = pipeline.get_pipeline_metadata()
            logger.info(f"Pipeline type: {result.get('pipeline_type')}")
            logger.info(f"Status: {result.get('status')}")
            logger.info(f"Airflow compatible: {result.get('is_airflow_compatible')}")
            
        elif args.sector:
            logger.info(f"Processing sector: {args.sector}")
            result = pipeline.get_sector_data(args.sector)
            format_result_summary(result)
            
        elif args.incremental:
            since_date = datetime.datetime.now() - datetime.timedelta(days=args.days)
            logger.info(f"Running incremental update since {since_date}")
            result = pipeline.run_incremental_update(since_date)
            format_result_summary(result)
            
        else:
            logger.info("Running full ETL pipeline")
            result = pipeline.run_full_pipeline()
            format_result_summary(result)
        
        return 0
    
    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
