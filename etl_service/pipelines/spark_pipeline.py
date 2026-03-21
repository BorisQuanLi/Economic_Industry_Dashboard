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
import os
import sys
import time

from pyspark.sql import SparkSession

from etl_service.src.adapters.spark_companies_builder import SparkCompaniesBuilder
from etl_service.src.adapters.spark_financials_reader import SparkFinancialsReader
from etl_service.src.adapters.aml_performance_utils import (
    apply_subsector_rolling_performance,
    enrich_companies_with_subsector_risk,
)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_NAME = os.getenv("DB_NAME", "investment_analysis")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "postgres")
JDBC_URL = f"jdbc:postgresql://{DB_HOST}:5432/{DB_NAME}"
DB_PROPERTIES = {"user": DB_USER, "password": DB_PASS, "driver": "org.postgresql.Driver"}

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
        """Two-stage AML analytics pipeline.

        Stage 1 (always runs): Wikipedia CSV → SparkCompaniesBuilder → AML risk ranking.
        Stage 2 (conditional): PostgreSQL → SparkFinancialsReader → rolling P/E window
        and broadcast join via aml_performance_utils. Skipped gracefully if the DB has
        not been populated by the standard pipeline yet.
        """
        logger.info("Starting PySpark AML analytics pipeline...")
        start_time = time.time()

        try:
            # ── Stage 1 ──────────────────────────────────────────────────────────
            builder = SparkCompaniesBuilder(self.spark)
            ranked_df = builder.run()  # extract → transform → rank → cache → run_analysis

            enriched_df = builder.join_sector_risk_profile(ranked_df)
            logger.info("Stage 1: company rows enriched with sector AML risk profile:")
            enriched_df.show(5, truncate=False)

            trend_df = builder.get_sector_growth_trend(ranked_df)
            logger.info("Stage 1: sector growth trend (lag window):")
            trend_df.select(
                "name", "sector", "year_founded", "number_of_employees", "employee_delta"
            ).show(10, truncate=False)

            # ── Stage 2 ──────────────────────────────────────────────────────────
            try:
                reader = SparkFinancialsReader(self.spark, JDBC_URL, DB_PROPERTIES)
                subsector_df = reader.get_subsector_financials()

                rolling_df = apply_subsector_rolling_performance(subsector_df)
                logger.info("Stage 2: rolling P/E window analytics:")
                rolling_df.show(10, truncate=False)

                enriched_financials = enrich_companies_with_subsector_risk(
                    ranked_df, subsector_df
                )
                logger.info("Stage 2: companies enriched with sub-sector risk benchmarks:")
                enriched_financials.show(5, truncate=False)

            except Exception as e:
                logger.warning(
                    f"Stage 2 skipped — DB not populated or JDBC unavailable: {e}"
                )

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
