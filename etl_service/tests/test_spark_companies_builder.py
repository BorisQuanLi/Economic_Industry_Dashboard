import logging
import pytest
from pyspark.sql import SparkSession
from etl_service.src.adapters.spark_companies_builder import SparkCompaniesBuilder

@pytest.fixture(scope="module")
def spark():
    """PySpark session fixture for testing."""
    session = SparkSession.builder \
        .master("local[1]") \
        .appName("PySparkUnitTests") \
        .config("spark.sql.adaptive.enabled", "false") \
        .getOrCreate()
    yield session
    session.stop()

def test_pyspark_analytics_logic(spark):
    """
    Test window function ranking and AML flagging logic in SparkCompaniesBuilder.
    """
    # 1. Setup Mock Data
    # This data is designed to test ranking within partitions and AML thresholds.
    data = [
        ("TechCorp", "TC", "Technology", "New York", 2000, 1000),
        ("Gigantor", "GG", "Technology", "California", 1995, 5000),
        ("SmallBank", "SB", "Finance", "Chicago", 2010, 200),
        ("MegaBank", "MB", "Finance", "New York", 1980, 100000)
    ]
    columns = ["name", "ticker", "sector", "hq_state", "year_founded", "number_of_employees"]
    df = spark.createDataFrame(data, columns)
    
    builder = SparkCompaniesBuilder(spark)

    # 2. Test Window Function (Ranking by employee size in sector)
    ranked_df = builder.get_transaction_risk_summary(df)
    results = ranked_df.orderBy("sector", "size_rank_in_sector").collect()
    
    # Expected ranking: Gigantor (5000) > TechCorp (1000) in Technology
    # Expected ranking: MegaBank (100k) > SmallBank (200) in Finance
    
    # Verify Gigantor is Rank 1 in Technology
    gigantor = next(r for r in results if r.name == "Gigantor")
    assert gigantor.size_rank_in_sector == 1, "Gigantor should be rank 1 in Technology"
    
    # Verify TechCorp is Rank 2 in Technology
    techcorp = next(r for r in results if r.name == "TechCorp")
    assert techcorp.size_rank_in_sector == 2, "TechCorp should be rank 2 in Technology"

    # Verify MegaBank is Rank 1 in Finance
    megabank = next(r for r in results if r.name == "MegaBank")
    assert megabank.size_rank_in_sector == 1, "MegaBank should be rank 1 in Finance"
    
    # 3. Test Sector Summary & AML Flagging Logic
    summary_df = builder.get_sector_summary(df)
    summary_results = summary_df.collect()
    
    # Finance average employees = (200 + 100000) / 2 = 50100, which is > 50k
    finance_summary = next(r for r in summary_results if r.sector == "Finance")
    assert finance_summary.aml_risk_flag == "High Capacity / Review Needed", \
        "Finance sector should be flagged due to high average employee count"
    
    # Technology average employees = (1000 + 5000) / 2 = 3000, which is < 50k
    tech_summary = next(r for r in summary_results if r.sector == "Technology")
    assert tech_summary.aml_risk_flag == "Standard", \
        "Technology sector should have a 'Standard' AML risk flag"

def test_data_quality_checks(spark):
    """
    Test data quality checks to ensure invalid records are filtered out.
    """
    # 1. Setup Mock Data with invalid records
    data = [
        ("ValidCorp", "VC", "ValidSector", "ValidState", 2020, 100),
        ("", "NV", "NoNameSector", "State", 2021, 50),          # Invalid: Empty name
        ("NoTicker", None, "NoTickerSector", "State", 2022, 75)  # Invalid: Null ticker
    ]
    columns = ["name", "ticker", "sector", "hq_state", "year_founded", "number_of_employees"]
    df = spark.createDataFrame(data, columns)

    builder = SparkCompaniesBuilder(spark)

    # 2. Apply data quality checks via the transform method
    # The _add_data_quality_checks is called within transform_companies_data
    
    # Mocking the transform_companies_data to isolate the quality check
    # For this test, we can directly call the "private" method, though it's not best practice.
    # A better approach would be to refactor it out if it were more complex.
    clean_df = builder._add_data_quality_checks(df)
    
    # 3. Verify that only the valid record remains
    assert clean_df.count() == 1, "Should only have one valid record after cleaning"
    
    # Verify the correct record is kept
    remaining_record = clean_df.collect()[0]
    assert remaining_record.name == "ValidCorp", "The remaining record should be ValidCorp"

def test_run_analysis_warns_on_high_risk_sector(spark, caplog):
    """run_analysis() should emit a WARNING when a high-risk sector is present."""
    data = [
        ("MegaBank", "MB", "Finance", "Diversified Banks", "New York", 1980, 100000),
        ("SmallBank", "SB", "Finance", "Regional Banks", "Chicago", 2010, 200),
        ("TechCorp", "TC", "Technology", "Software", "New York", 2000, 1000),
    ]
    columns = ["name", "ticker", "sector", "sub_industry", "hq_state", "year_founded", "number_of_employees"]
    df = spark.createDataFrame(data, columns)

    builder = SparkCompaniesBuilder(spark)
    ranked_df = builder.get_transaction_risk_summary(df)

    with caplog.at_level(logging.WARNING, logger="etl_service.src.adapters.spark_companies_builder"):
        builder.run_analysis(ranked_df)

    assert "HIGH RISK SECTORS IDENTIFIED" in caplog.text

def test_get_sector_growth_trend(spark):
    """lag() should populate prev_employees and compute employee_delta per sector."""
    data = [
        ("OldBank",  "OB", "Finance",    "Banks",    "NY", 1980, 50000),
        ("NewBank",  "NB", "Finance",    "Banks",    "NJ", 2000, 80000),
        ("TechCorp", "TC", "Technology", "Software", "CA", 1995, 5000),
    ]
    columns = ["name", "ticker", "sector", "sub_industry", "hq_state", "year_founded", "number_of_employees"]
    df = spark.createDataFrame(data, columns)

    builder = SparkCompaniesBuilder(spark)
    result = builder.get_sector_growth_trend(df).orderBy("sector", "year_founded").collect()

    # OldBank is first in Finance — no predecessor, delta should be null
    old_bank = next(r for r in result if r.name == "OldBank")
    assert old_bank.prev_employees_in_sector is None
    assert old_bank.employee_delta is None

    # NewBank follows OldBank — delta = 80000 - 50000
    new_bank = next(r for r in result if r.name == "NewBank")
    assert new_bank.employee_delta == 30000


def test_join_sector_risk_profile(spark):
    """Each company row should be enriched with its sector's aml_risk_flag."""
    data = [
        ("MegaBank", "MB", "Finance",    "Banks",    "NY", 1980, 100000),
        ("SmallBank","SB", "Finance",    "Banks",    "IL", 2010, 200),
        ("TechCorp", "TC", "Technology", "Software", "CA", 2000, 1000),
    ]
    columns = ["name", "ticker", "sector", "sub_industry", "hq_state", "year_founded", "number_of_employees"]
    df = spark.createDataFrame(data, columns)

    builder = SparkCompaniesBuilder(spark)
    result = builder.join_sector_risk_profile(df).collect()

    finance_rows = [r for r in result if r.sector == "Finance"]
    # All Finance rows should carry the sector-level flag
    assert all(r.aml_risk_flag == "High Capacity / Review Needed" for r in finance_rows)

    tech_rows = [r for r in result if r.sector == "Technology"]
    assert all(r.aml_risk_flag == "Standard" for r in tech_rows)
