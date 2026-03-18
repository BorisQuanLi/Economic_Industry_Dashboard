import pytest
from pyspark.sql import Row
# Use relative import if running inside the package, 
# or keep as is if running with 'python -m pytest'
from src.adapters.aml_performance_utils import (
    apply_subsector_rolling_performance, 
    enrich_companies_with_subsector_risk
)

def test_apply_subsector_rolling_performance(spark_session):
    data = [
        Row(sub_industry_gics="Software", year=2021, avg_price_earnings_ratio=20.0, avg_closing_price=100.0),
        Row(sub_industry_gics="Software", year=2022, avg_price_earnings_ratio=30.0, avg_closing_price=150.0),
        Row(sub_industry_gics="Software", year=2023, avg_price_earnings_ratio=40.0, avg_closing_price=200.0),
        Row(sub_industry_gics="Software", year=2024, avg_price_earnings_ratio=10.0, avg_closing_price=50.0),
    ]
    df = spark_session.createDataFrame(data)

    result_df = apply_subsector_rolling_performance(df).orderBy("year")
    results = result_df.collect()

    # Accessing results by index for Row objects
    assert results[0]["rolling_avg_pe_2yr"] == 20.0
    assert results[1]["rolling_avg_pe_2yr"] == 25.0
    assert results[2]["rolling_avg_pe_2yr"] == 30.0
    # 2024 checks rangeBetween(-2, 0): (30 + 40 + 10) / 3 = 26.67
    # Access the 4th row (index 3) for the year 2024
    assert results[3]["rolling_avg_pe_2yr"] == 26.67

def test_enrich_companies_with_subsector_risk(spark_session):
    companies_data = [Row(name="Company A", sub_industry_gics="Software")]
    risk_data = [Row(sub_industry_gics="Software", sector_risk_score=0.85)]
    
    companies_df = spark_session.createDataFrame(companies_data)
    risk_df = spark_session.createDataFrame(risk_data)
    
    enriched_df = enrich_companies_with_subsector_risk(companies_df, risk_df)
    result = enriched_df.collect()[0]
    
    assert result["sector_risk_score"] == 0.85
