#!/usr/bin/env python3
"""
PySpark ETL Pipeline — AML / Financial Crimes Analytics Demo

Orchestrates the full pipeline via SparkCompaniesBuilder, demonstrating:
  - Window functions (rank, lag)
  - DataFrame join
  - Explicit groupBy/agg with AML outlier flagging
  - .cache() for DAG optimisation

Usage:
    python -m pipelines.spark_pipeline [--spark-mode local]
"""

import argparse
import logging
import sys
import time

from pyspark.sql import SparkSession

from etl_service.src.adapters.spark_companies_builder import SparkCompaniesBuilder

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class SparkETLPipeline:
    def __init__(self, spark_mode: str = "local[*]"):
        self.spark = SparkSession.builder \
            .appName("S&P500-AML-ETL") \
            .master(spark_mode) \
            .config("spark.sql.adaptive.enabled", "true") \
            .config("spark.sql.adaptive.coalescePartitions.enabled", "true") \
            .getOrCreate()
        self.spark.sparkContext.setLogLevel("WARN")
        logger.info(f"Spark session initialised in {spark_mode} mode")

    def run_companies_pipeline(self):
        """End-to-end AML analytics demo using SparkCompaniesBuilder."""
        logger.info("Starting PySpark AML analytics pipeline...")
        start_time = time.time()

        try:
            builder = SparkCompaniesBuilder(self.spark)
            ranked_df = builder.run()  # extract → transform → rank → cache → run_analysis

            # Join: enrich each company row with sector-level AML risk profile
            enriched_df = builder.join_sector_risk_profile(ranked_df)
            logger.info("Company rows enriched with sector AML risk profile:")
            enriched_df.show(5, truncate=False)

            # Lag window: employee delta / velocity per sector
            trend_df = builder.get_sector_growth_trend(ranked_df)
            logger.info("Sector growth trend (lag window):")
            trend_df.select(
                "name", "sector", "year_founded", "number_of_employees", "employee_delta"
            ).show(10, truncate=False)

            logger.info(f"Pipeline completed in {time.time() - start_time:.2f}s")

        except Exception as e:
            logger.error(f"Pipeline failed: {e}")
            raise

    def stop(self):
        if self.spark:
            self.spark.stop()


def main():
    parser = argparse.ArgumentParser(description="PySpark AML Analytics Pipeline")
    parser.add_argument('--spark-mode', default='local[*]')
    args = parser.parse_args()

    pipeline = None
    try:
        pipeline = SparkETLPipeline(spark_mode=args.spark_mode)
        pipeline.run_companies_pipeline()
    except Exception as e:
        logger.error(f"Pipeline execution failed: {e}")
        sys.exit(1)
    finally:
        if pipeline:
            pipeline.stop()


if __name__ == "__main__":
    main()
