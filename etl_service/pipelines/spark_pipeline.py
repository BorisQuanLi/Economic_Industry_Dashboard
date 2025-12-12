#!/usr/bin/env python3
"""
PySpark ETL Pipeline Runner for S&P 500 Financial Data

This script orchestrates the complete ETL pipeline using Apache Spark:
1. Initialize Spark session
2. Ingest S&P 500 company list from Wikipedia using Spark DataFrames
3. Process and transform data using Spark operations
4. Write to PostgreSQL using Spark JDBC

Usage:
    python run_pipeline_spark.py [--spark-mode local] [--init-db] [--companies-only]

Examples:
    python run_pipeline_spark.py --spark-mode local --init-db
    python run_pipeline_spark.py --companies-only
"""

import argparse
import logging
import sys
import time
from typing import Optional

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, regexp_extract, split
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

from etl_service.src.db.db import get_db, close_db
from etl_service.src.adapters.wiki_page_client import WikiPageClient
from etl_service.settings import DATABASE_URL

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SparkETLPipeline:
    def __init__(self, spark_mode: str = "local[*]"):
        self.spark_mode = spark_mode
        self.spark = None
        self._init_spark_session()
    
    def _init_spark_session(self):
        """Initialize Spark session with PostgreSQL JDBC driver."""
        logger.info(f"Initializing Spark session in {self.spark_mode} mode...")
        
        self.spark = SparkSession.builder \
            .appName("S&P500-ETL-Pipeline") \
            .master(self.spark_mode) \
            .config("spark.jars.packages", "org.postgresql:postgresql:42.7.0") \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info("Spark session initialized successfully")
    
    def init_database(self):
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
    
    def extract_sp500_companies(self):
        """Extract S&P 500 companies using Spark DataFrames."""
        logger.info("Extracting S&P 500 companies from Wikipedia...")
        
        try:
            # Get raw data from Wikipedia
            wiki_client = WikiPageClient()
            companies_data = wiki_client.get_sp500_companies()
            
            # Convert to Spark DataFrame
            df = self.spark.createDataFrame(companies_data)
            
            logger.info(f"Extracted {df.count()} companies")
            return df
            
        except Exception as e:
            logger.error(f"Failed to extract companies: {e}")
            raise
    
    def transform_companies_data(self, df):
        """Transform companies data using Spark operations."""
        logger.info("Transforming companies data...")
        
        # Clean and transform data
        transformed_df = df.select(
            col("Security").alias("name"),
            col("Ticker").alias("ticker"),
            col("GICS Sector").alias("sector"),
            col("GICS Sub-Industry").alias("sub_industry"),
            col("Headquarters Location").alias("headquarters"),
            col("Founded").alias("year_founded")
        ).withColumn(
            "hq_state",
            when(col("headquarters").contains(", "), 
                 split(col("headquarters"), ", ").getItem(1))
            .otherwise(col("headquarters"))
        ).withColumn(
            "year_founded",
            when(col("year_founded").rlike("^\\d{4}$"), 
                 col("year_founded").cast(IntegerType()))
            .otherwise(-1)
        )
        
        logger.info("Data transformation completed")
        return transformed_df
    
    def load_to_postgresql(self, df, table_name: str):
        """Load DataFrame to PostgreSQL using Spark JDBC."""
        logger.info(f"Loading data to PostgreSQL table: {table_name}")
        
        # Parse DATABASE_URL for JDBC connection
        # Format: postgresql://user:password@host:port/database
        db_parts = DATABASE_URL.replace("postgresql://", "").split("/")
        db_name = db_parts[1]
        host_port_user = db_parts[0].split("@")
        host_port = host_port_user[1]
        user_pass = host_port_user[0].split(":")
        
        jdbc_url = f"jdbc:postgresql://{host_port}/{db_name}"
        
        properties = {
            "user": user_pass[0],
            "password": user_pass[1],
            "driver": "org.postgresql.Driver"
        }
        
        try:
            df.write \
                .mode("append") \
                .jdbc(jdbc_url, table_name, properties=properties)
            
            logger.info(f"Successfully loaded {df.count()} records to {table_name}")
            
        except Exception as e:
            logger.error(f"Failed to load data to PostgreSQL: {e}")
            raise
    
    def run_companies_pipeline(self):
        """Run the complete companies ETL pipeline."""
        logger.info("Starting PySpark companies ETL pipeline...")
        start_time = time.time()
        
        try:
            # Extract
            companies_df = self.extract_sp500_companies()
            
            # Transform
            transformed_df = self.transform_companies_data(companies_df)
            
            # Show sample data
            logger.info("Sample transformed data:")
            transformed_df.show(5, truncate=False)
            
            # Load (commented out for now - requires proper table setup)
            # self.load_to_postgresql(transformed_df, "companies")
            
            elapsed = time.time() - start_time
            logger.info(f"PySpark ETL pipeline completed in {elapsed:.2f} seconds")
            
        except Exception as e:
            logger.error(f"PySpark ETL pipeline failed: {e}")
            raise
    
    def stop(self):
        """Stop Spark session."""
        if self.spark:
            self.spark.stop()
            logger.info("Spark session stopped")


def main():
    parser = argparse.ArgumentParser(description="Run S&P 500 PySpark ETL Pipeline")
    parser.add_argument(
        '--spark-mode',
        type=str,
        default='local[*]',
        help='Spark master mode (default: local[*])'
    )
    parser.add_argument(
        '--init-db',
        action='store_true',
        help='Initialize database schema before loading data'
    )
    parser.add_argument(
        '--companies-only',
        action='store_true',
        help='Only process companies data'
    )
    
    args = parser.parse_args()
    
    pipeline = None
    try:
        pipeline = SparkETLPipeline(spark_mode=args.spark_mode)
        
        if args.init_db:
            pipeline.init_database()
        
        if args.companies_only:
            pipeline.run_companies_pipeline()
        else:
            # Future: Add financial data processing
            pipeline.run_companies_pipeline()
            
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        sys.exit(1)
    finally:
        if pipeline:
            pipeline.stop()
        close_db()


if __name__ == "__main__":
    main()