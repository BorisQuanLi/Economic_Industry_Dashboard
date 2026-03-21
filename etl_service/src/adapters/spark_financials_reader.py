"""
SparkFinancialsReader — reads quarterly_reports and prices_pe from PostgreSQL
via JDBC and produces a DataFrame compatible with aml_performance_utils.

Requires the standard pipeline to have populated the DB first.
Stage 2 of the two-stage Spark analytics pipeline:

  Stage 1: Wikipedia CSV → SparkCompaniesBuilder → AML risk ranking
  Stage 2: PostgreSQL    → SparkFinancialsReader  → rolling P/E window + broadcast join
"""

import logging
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql.functions import avg, col

logger = logging.getLogger(__name__)


class SparkFinancialsReader:
    def __init__(self, spark: SparkSession, jdbc_url: str, db_properties: dict):
        """
        Args:
            spark: active SparkSession
            jdbc_url: e.g. "jdbc:postgresql://localhost:5432/investment_analysis"
            db_properties: {"user": ..., "password": ..., "driver": "org.postgresql.Driver"}
        """
        self.spark = spark
        self.jdbc_url = jdbc_url
        self.db_properties = db_properties

    def _read_table(self, table: str) -> DataFrame:
        return self.spark.read.jdbc(
            url=self.jdbc_url,
            table=table,
            properties=self.db_properties
        )

    def get_subsector_financials(self) -> DataFrame:
        """
        Join quarterly_reports → prices_pe → companies → sub_industries to produce
        a DataFrame with the schema expected by aml_performance_utils:

            sub_industry_gics | year | avg_price_earnings_ratio | avg_closing_price

        This is the input surface for apply_subsector_rolling_performance() and
        enrich_companies_with_subsector_risk().
        """
        logger.info("Reading financials tables from PostgreSQL via JDBC...")

        prices = self._read_table("prices_pe")
        quarterly = self._read_table("quarterly_reports")
        companies = self._read_table("companies").select("id", "sub_industry_id")
        sub_industries = self._read_table("sub_industries").select(
            col("id").alias("sub_id"),
            col("sub_industry_GICS").alias("sub_industry_gics")
        )

        joined = (
            prices
            .join(quarterly, on="company_id", how="inner")
            .join(companies, prices["company_id"] == companies["id"], how="inner")
            .join(sub_industries, col("sub_industry_id") == col("sub_id"), how="inner")
        )

        return joined.groupBy("sub_industry_gics", "year").agg(
            avg("price_earnings_ratio").alias("avg_price_earnings_ratio"),
            avg("closing_price").alias("avg_closing_price")
        )
