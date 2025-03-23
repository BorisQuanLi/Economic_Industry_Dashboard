#!/usr/bin/env python
"""
CLI entrypoint for the S&P 500 ETL Pipeline.

This module provides a convenient command-line interface to run the ETL pipeline
with various options. It serves as a thin wrapper around the main pipeline implementation.

Usage:
    python run_pipeline.py --env=dev
    python run_pipeline.py --incremental --days=2
    python run_pipeline.py --sector=Technology
"""

import argparse
import logging
import sys
import datetime
from typing import Optional

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

def main():
    """Main entry point for the CLI"""
    parser = argparse.ArgumentParser(description='S&P 500 ETL Pipeline')
    parser.add_argument('--env', default='dev', help='Environment (dev/test/prod)')
    parser.add_argument('--incremental', action='store_true', help='Run incremental update')
    parser.add_argument('--days', type=int, default=1, help='Days to look back for incremental update')
    parser.add_argument('--sector', help='Process a specific sector only')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose logging')
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(args.verbose)
    
    try:
        # Initialize pipeline with proper configuration
        config = get_config(args.env)
        pipeline = SP500ETLPipeline(config)
        
        # Select operation mode
        if args.sector:
            logger.info(f"Processing sector: {args.sector}")
            result = pipeline.get_sector_data(args.sector)
        elif args.incremental:
            since_date = datetime.datetime.now() - datetime.timedelta(days=args.days)
            logger.info(f"Running incremental update since {since_date}")
            result = pipeline.run_incremental_update(since_date)
        else:
            logger.info("Running full ETL pipeline")
            result = pipeline.run_full_pipeline()
        
        # Log summary of operation
        if isinstance(result, dict) and 'status' in result:
            logger.info(f"Pipeline complete: {result['status']}")
            if 'records_processed' in result and 'duration_seconds' in result:
                logger.info(f"Processed {result['records_processed']} records in {result['duration_seconds']:.2f} seconds")
        else:
            logger.info("Operation completed successfully")
        
        return 0
    
    except Exception as e:
        logger.error(f"Pipeline failed with error: {str(e)}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1

if __name__ == "__main__":
    sys.exit(main())
