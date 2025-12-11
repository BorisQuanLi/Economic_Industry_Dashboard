"""
PySpark-based S&P 500 Companies Builder

This module handles the extraction, transformation, and loading of S&P 500 company data
using Apache Spark for distributed processing.
"""

import logging
from typing import Optional
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import col, when, split, regexp_extract, trim, coalesce, lit
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

from etl_service.src.adapters.wiki_page_client import WikiPageClient

logger = logging.getLogger(__name__)


class SparkCompaniesBuilder:
    """PySpark-based builder for S&P 500 companies data processing."""
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.wiki_client = WikiPageClient()
    
    def extract_companies_data(self) -> DataFrame:
        """Extract S&P 500 companies data from Wikipedia."""
        logger.info("Extracting S&P 500 companies from Wikipedia...")
        
        try:
            # Get raw data from Wikipedia client
            companies_data = self.wiki_client.get_sp500_companies()
            
            # Convert to Spark DataFrame
            df = self.spark.createDataFrame(companies_data)
            
            logger.info(f"Successfully extracted {df.count()} companies")
            return df
            
        except Exception as e:
            logger.error(f"Failed to extract companies data: {e}")
            raise
    
    def transform_companies_data(self, df: DataFrame) -> DataFrame:
        """Transform companies data using Spark operations."""
        logger.info("Transforming companies data with PySpark...")
        
        try:
            # Define the transformation pipeline
            transformed_df = df.select(
                # Basic company information
                trim(col("Security")).alias("name"),
                trim(col("Ticker")).alias("ticker"),
                trim(col("GICS Sector")).alias("sector"),
                trim(col("GICS Sub-Industry")).alias("sub_industry"),
                
                # Parse headquarters location
                col("Headquarters Location").alias("headquarters_raw"),
                
                # Handle founded year
                col("Founded").alias("founded_raw"),
                
                # Additional fields
                coalesce(col("Employees"), lit(-1)).alias("employees")
                
            ).withColumn(
                # Extract state from headquarters (handle "City, State" format)
                "hq_state",
                when(col("headquarters_raw").contains(", "), 
                     split(col("headquarters_raw"), ", ").getItem(1))
                .otherwise(col("headquarters_raw"))
                
            ).withColumn(
                # Clean and convert founded year
                "year_founded",
                when(col("founded_raw").rlike("^\\d{4}$"), 
                     col("founded_raw").cast(IntegerType()))
                .otherwise(-1)
                
            ).withColumn(
                # Clean employees count
                "number_of_employees",
                when(col("employees").isNotNull() & (col("employees") != ""), 
                     col("employees").cast(IntegerType()))
                .otherwise(-1)
                
            ).select(
                # Final column selection
                col("name"),
                col("ticker"),
                col("sector"),
                col("sub_industry"),
                col("hq_state"),
                col("year_founded"),
                col("number_of_employees")
            )
            
            # Add data quality checks
            transformed_df = self._add_data_quality_checks(transformed_df)
            
            logger.info("Data transformation completed successfully")
            return transformed_df
            
        except Exception as e:
            logger.error(f"Failed to transform companies data: {e}")
            raise
    
    def _add_data_quality_checks(self, df: DataFrame) -> DataFrame:
        """Add data quality validation and cleaning."""
        logger.info("Applying data quality checks...")
        
        # Filter out invalid records
        clean_df = df.filter(
            (col("name").isNotNull()) & 
            (col("ticker").isNotNull()) &
            (col("name") != "") &
            (col("ticker") != "")
        )
        
        # Log data quality metrics
        original_count = df.count()
        clean_count = clean_df.count()
        
        if original_count != clean_count:
            logger.warning(f"Data quality check: {original_count - clean_count} invalid records removed")
        
        return clean_df
    
    def get_sector_summary(self, df: DataFrame) -> DataFrame:
        """Generate sector summary statistics."""
        logger.info("Generating sector summary...")
        
        sector_summary = df.groupBy("sector") \
            .agg(
                {"*": "count", 
                 "year_founded": "avg",
                 "number_of_employees": "avg"}
            ) \
            .withColumnRenamed("count(1)", "company_count") \
            .withColumnRenamed("avg(year_founded)", "avg_founded_year") \
            .withColumnRenamed("avg(number_of_employees)", "avg_employees") \
            .orderBy(col("company_count").desc())
        
        return sector_summary
    
    def get_sub_industry_summary(self, df: DataFrame) -> DataFrame:
        """Generate sub-industry summary statistics."""
        logger.info("Generating sub-industry summary...")
        
        sub_industry_summary = df.groupBy("sector", "sub_industry") \
            .agg({"*": "count"}) \
            .withColumnRenamed("count(1)", "company_count") \
            .orderBy(col("sector"), col("company_count").desc())
        
        return sub_industry_summary
    
    def run_analysis(self, df: DataFrame):
        """Run comprehensive analysis on companies data."""
        logger.info("Running comprehensive companies analysis...")
        
        # Basic statistics
        total_companies = df.count()
        logger.info(f"Total companies processed: {total_companies}")
        
        # Sector analysis
        sector_summary = self.get_sector_summary(df)
        logger.info("Sector distribution:")
        sector_summary.show(20, truncate=False)
        
        # Sub-industry analysis
        sub_industry_summary = self.get_sub_industry_summary(df)
        logger.info("Top sub-industries by company count:")
        sub_industry_summary.show(10, truncate=False)
        
        # Data quality metrics
        null_tickers = df.filter(col("ticker").isNull()).count()
        null_names = df.filter(col("name").isNull()).count()
        
        logger.info(f"Data quality metrics:")
        logger.info(f"  - Records with null tickers: {null_tickers}")
        logger.info(f"  - Records with null names: {null_names}")
    
    def run(self) -> DataFrame:
        """Run the complete companies ETL process."""
        logger.info("Starting PySpark companies ETL process...")
        
        try:
            # Extract
            raw_df = self.extract_companies_data()
            
            # Transform
            transformed_df = self.transform_companies_data(raw_df)
            
            # Analysis
            self.run_analysis(transformed_df)
            
            logger.info("PySpark companies ETL process completed successfully")
            return transformed_df
            
        except Exception as e:
            logger.error(f"PySpark companies ETL process failed: {e}")
            raise