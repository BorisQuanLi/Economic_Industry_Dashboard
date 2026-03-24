"""
Tests for SparkFinancialsReader.

JDBC reads are replaced with spark.createDataFrame() so no live DB is required.
"""
import pytest
from unittest.mock import patch
from pyspark.sql import SparkSession, Row

from etl_service.src.adapters.spark_financials_reader import SparkFinancialsReader


@pytest.fixture(scope="module")
def spark():
    session = SparkSession.builder \
        .master("local[1]") \
        .appName("SparkFinancialsReaderTests") \
        .config("spark.sql.adaptive.enabled", "false") \
        .getOrCreate()
    yield session
    session.stop()


def _make_reader(spark):
    return SparkFinancialsReader(
        spark,
        jdbc_url="jdbc:postgresql://localhost:5432/test",
        db_properties={"user": "test", "password": "test", "driver": "org.postgresql.Driver"},
    )


def test_get_subsector_financials_schema(spark):
    """Output DataFrame must have the four columns aml_performance_utils expects."""
    prices = spark.createDataFrame([
        Row(company_id=1, price_earnings_ratio=20.0, closing_price=150.0, year=2023),
        Row(company_id=2, price_earnings_ratio=30.0, closing_price=200.0, year=2023),
    ])
    quarterly = spark.createDataFrame([
        Row(company_id=1, revenue=1000000),
        Row(company_id=2, revenue=2000000),
    ])
    companies = spark.createDataFrame([
        Row(id=1, sub_industry_id=10),
        Row(id=2, sub_industry_id=10),
    ])
    sub_industries = spark.createDataFrame([
        Row(id=10, sub_industry_GICS="Application Software"),
    ])

    reader = _make_reader(spark)

    # Patch _read_table to return our mock DataFrames
    table_map = {
        "prices_pe": prices,
        "quarterly_reports": quarterly,
        "companies": companies,
        "sub_industries": sub_industries,
    }
    with patch.object(reader, "_read_table", side_effect=lambda t: table_map[t]):
        result = reader.get_subsector_financials()

    cols = set(result.columns)
    assert {"sub_industry_gics", "year", "avg_price_earnings_ratio", "avg_closing_price"} <= cols


def test_get_subsector_financials_aggregation(spark):
    """avg_price_earnings_ratio should be the mean across companies in the sub-sector."""
    prices = spark.createDataFrame([
        Row(company_id=1, price_earnings_ratio=20.0, closing_price=100.0, year=2023),
        Row(company_id=2, price_earnings_ratio=40.0, closing_price=200.0, year=2023),
    ])
    quarterly = spark.createDataFrame([
        Row(company_id=1, revenue=1000000),
        Row(company_id=2, revenue=2000000),
    ])
    companies = spark.createDataFrame([
        Row(id=1, sub_industry_id=10),
        Row(id=2, sub_industry_id=10),
    ])
    sub_industries = spark.createDataFrame([
        Row(id=10, sub_industry_GICS="Application Software"),
    ])

    reader = _make_reader(spark)
    table_map = {
        "prices_pe": prices,
        "quarterly_reports": quarterly,
        "companies": companies,
        "sub_industries": sub_industries,
    }
    with patch.object(reader, "_read_table", side_effect=lambda t: table_map[t]):
        result = reader.get_subsector_financials().collect()

    assert len(result) == 1
    row = result[0]
    assert row["sub_industry_gics"] == "Application Software"
    assert row["avg_price_earnings_ratio"] == pytest.approx(30.0)
    assert row["avg_closing_price"] == pytest.approx(150.0)
