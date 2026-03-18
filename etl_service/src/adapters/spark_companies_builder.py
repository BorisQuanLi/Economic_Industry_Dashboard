"""
PySpark-based S&P 500 Companies Builder

This module handles the extraction, transformation, and loading of S&P 500 company data
using Apache Spark for distributed processing.
"""

import logging
import os
from pyspark.sql import SparkSession, DataFrame, Window
from pyspark.sql.functions import (
    col, when, split, regexp_extract, trim, coalesce, lit,
    rank, lag, avg, count, sum as spark_sum
)
from pyspark.sql.types import StructType, StructField, StringType, IntegerType

from etl_service.src.adapters.wiki_page_client import get_sp500_wiki_data

# Set the absolute filepath for the first data source in the ETL pipeline
BASE_DIR = os.getenv("DATA_DIR", os.path.dirname(os.path.abspath(__file__)))
# Use BASE_DIR to ensure the path is consistent
sp500_wiki_data_filepath = os.path.join(BASE_DIR, "data/sp500_stocks_wiki_info.csv")

logger = logging.getLogger(__name__)


class SparkCompaniesBuilder:
    """PySpark-based builder for S&P 500 companies data processing."""
    
    def __init__(self, spark: SparkSession):
        self.spark = spark
        self.wiki_client = get_sp500_wiki_data()
    
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
    
    def get_transaction_risk_summary(self, df: DataFrame) -> DataFrame:
        """
        Rank companies by employee count within each sector using window functions.
        This helps identify high-impact entities for risk assessment.
        """
        logger.info("Ranking companies by size within sectors...")
        
        # Define the window: group by sector, order by employee count descending
        window_spec = Window.partitionBy("sector").orderBy(col("number_of_employees").desc())
        
        return df.withColumn("size_rank_in_sector", rank().over(window_spec))

    def get_sector_growth_trend(self, df: DataFrame) -> DataFrame:
        """
        Use lag() window function to compute employee count change vs. the
        previously-founded company in the same sector (ordered by founding year).
        Negative delta flags shrinking entities — relevant for AML risk velocity checks.
        """
        logger.info("Computing sector growth trends with lag()...")
        window_spec = Window.partitionBy("sector").orderBy(col("year_founded"))
        return df.withColumn(
            "prev_employees_in_sector",
            lag("number_of_employees", 1).over(window_spec)
        ).withColumn(
            "employee_delta",
            col("number_of_employees") - col("prev_employees_in_sector")
        )

    def join_sector_risk_profile(self, df: DataFrame) -> DataFrame:
        """
        Join company-level data with sector-level AML risk summary.
        Demonstrates Spark DataFrame join — enriches each row with its sector's
        aggregate risk flag and avg employee count.
        """
        logger.info("Joining company data with sector risk profile...")
        sector_profile = self.get_sector_summary(df).select(
            "sector", "avg_employees", "aml_risk_flag"
        )
        return df.join(sector_profile, on="sector", how="left")

    def get_sector_summary(self, df: DataFrame) -> DataFrame:
        """Generate sector summary statistics using explicit named-function style."""
        logger.info("Generating sector summary (Refactored)...")

        # Refactored to use explicit count() and avg() functions
        sector_summary = df.groupBy("sector") \
            .agg(
                count("*").alias("company_count"),
                avg("year_founded").alias("avg_founded_year"),
                avg("number_of_employees").alias("avg_employees")
            ) \
            .orderBy(col("company_count").desc())

        # 3. AML Outlier Logic: Flag sectors with unusually high average employee counts
        # e.g., sectors where avg_employees > 50,000 are flagged as 'High Capacity'
        sector_summary = sector_summary.withColumn(
            "aml_risk_flag",
            when(col("avg_employees") > 50000, lit("High Capacity / Review Needed"))
            .otherwise(lit("Standard"))
        )

        return sector_summary
    
    def get_sub_industry_summary(self, df: DataFrame) -> DataFrame:
        """Generate sub-industry summary statistics."""
        logger.info("Generating sub-industry summary...")
        
        sub_industry_summary = df.groupBy("sector", "sub_industry") \
            .agg(count("*").alias("company_count")) \
            .orderBy(col("sector"), col("company_count").desc())
        
        return sub_industry_summary
    
    def run_analysis(self, df: DataFrame):
        """Showcase AML Risk flags and Sector Rankings.
        Run comprehensive analysis on companies data."""
        logger.info("Running comprehensive companies analysis...")
        
        # Show high-risk sectors first
        risk_summary = self.get_sector_summary(df)
        high_risk = risk_summary.filter(col("aml_risk_flag") != "Standard")
        
        if high_risk.count() > 0:
            logger.warning("HIGH RISK SECTORS IDENTIFIED:")
            high_risk.show()
        
        # Show top-ranked companies per sector
        df.filter(col("size_rank_in_sector") <= 3).show()

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
        """Run the complete companies ETL process with advanced analytics."""
        logger.info("Starting Enhanced PySpark ETL process...")

        try:
            raw_df = self.extract_companies_data()
            transformed_df = self.transform_companies_data(raw_df)

            # New Analytics: Risk Ranking
            ranked_df = self.get_transaction_risk_summary(transformed_df)
            ranked_df.cache()  # Avoid DAG re-computation — ranked_df used twice below
            
            # Updated Analysis (includes AML flags)
            self.run_analysis(ranked_df)

            logger.info("PySpark companies ETL process completed successfully")
            return ranked_df
            
        except Exception as e:
            logger.error(f"PySpark companies ETL process failed: {e}")
            raise