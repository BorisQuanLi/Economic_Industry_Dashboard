import pytest
from pyspark.sql import SparkSession

@pytest.fixture(scope="session")
def spark_session():
    """
    Provides a local SparkSession for the entire test suite.
    """
    session = SparkSession.builder \
        .master("local[1]") \
        .appName("EID-Unit-Tests") \
        .config("spark.sql.shuffle.partitions", "1") \
        .config("spark.ui.enabled", "false") \
        .getOrCreate()
    
    yield session
    session.stop()
