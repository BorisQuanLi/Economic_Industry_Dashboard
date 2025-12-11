#!/usr/bin/env python3
"""
ETL Pipeline Runner for S&P 500 Financial Data

This script orchestrates the complete ETL pipeline:
1. Initialize database schema (create tables)
2. Ingest S&P 500 company list from Wikipedia
3. Fetch quarterly financials from Financial Modeling Prep API
4. Fetch price/PE data from Financial Modeling Prep API

Usage:
    python run_pipeline.py [--init-db] [--sectors SECTOR1,SECTOR2,...]

Examples:
    python run_pipeline.py --init-db                    # Initialize DB and load all data
    python run_pipeline.py --sectors "Technology"       # Load only Technology sector
    python run_pipeline.py                              # Load all sectors (skip if exists)
"""

import argparse
import logging
import sys
import time

from etl_service.src.db.db import get_db, close_db
from etl_service.src.adapters.run_adapters import BuildSP500Companies, BuildQuarterlyReportsPricesPE
from etl_service.settings import API_KEY

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Available GICS Sectors
GICS_SECTORS = [
    "Information Technology",
    "Health Care", 
    "Financials",
    "Consumer Discretionary",
    "Communication Services",
    "Industrials",
    "Consumer Staples",
    "Energy",
    "Utilities",
    "Real Estate",
    "Materials"
]


def init_database():
    """Initialize database tables from migration SQL."""
    logger.info("Initializing database schema...")
    conn = get_db()
    cursor = conn.cursor()
    
    migration_path = "/app/etl_service/src/db/migrations/create_tables.sql"
    try:
        with open(migration_path, 'r') as f:
            sql = f.read()
        cursor.execute(sql)
        conn.commit()
        logger.info("Database schema initialized successfully")
    except FileNotFoundError:
        logger.error(f"Migration file not found: {migration_path}")
        raise
    except Exception as e:
        conn.rollback()
        logger.error(f"Failed to initialize database: {e}")
        raise
    finally:
        cursor.close()


def load_companies():
    """Load S&P 500 companies from Wikipedia."""
    logger.info("Loading S&P 500 companies from Wikipedia...")
    try:
        builder = BuildSP500Companies()
        builder.run()
        logger.info("Companies loaded successfully")
    except Exception as e:
        logger.error(f"Failed to load companies: {e}")
        raise


def load_sector_data(sector_name: str):
    """Load quarterly financials and price/PE data for a sector."""
    logger.info(f"Loading data for sector: {sector_name}")
    
    if API_KEY == "YOUR_FMP_API_KEY":
        logger.warning("FMP_API_KEY not set - skipping financial data fetch")
        return
    
    conn = get_db()
    cursor = conn.cursor()
    
    try:
        builder = BuildQuarterlyReportsPricesPE(conn, cursor)
        builder.run(sector_name)
        logger.info(f"Data loaded for sector: {sector_name}")
    except Exception as e:
        logger.error(f"Failed to load data for {sector_name}: {e}")
        raise
    finally:
        cursor.close()


def run_full_pipeline(sectors: list = None, init_db: bool = False):
    """Run the complete ETL pipeline."""
    logger.info("Starting ETL pipeline...")
    start_time = time.time()
    
    try:
        if init_db:
            init_database()
        
        load_companies()
        
        target_sectors = sectors if sectors else GICS_SECTORS
        for sector in target_sectors:
            load_sector_data(sector)
            time.sleep(1)  # Rate limiting for API calls
        
        elapsed = time.time() - start_time
        logger.info(f"ETL pipeline completed in {elapsed:.2f} seconds")
        
    except Exception as e:
        logger.error(f"ETL pipeline failed: {e}")
        sys.exit(1)
    finally:
        close_db()


def main():
    parser = argparse.ArgumentParser(description="Run S&P 500 ETL Pipeline")
    parser.add_argument(
        '--init-db', 
        action='store_true',
        help='Initialize database schema before loading data'
    )
    parser.add_argument(
        '--sectors',
        type=str,
        help='Comma-separated list of sectors to load (default: all)'
    )
    parser.add_argument(
        '--companies-only',
        action='store_true',
        help='Only load companies (skip financial data)'
    )
    
    args = parser.parse_args()
    
    sectors = None
    if args.sectors:
        sectors = [s.strip() for s in args.sectors.split(',')]
    
    if args.companies_only:
        if args.init_db:
            init_database()
        load_companies()
        close_db()
    else:
        run_full_pipeline(sectors=sectors, init_db=args.init_db)


if __name__ == "__main__":
    main()
