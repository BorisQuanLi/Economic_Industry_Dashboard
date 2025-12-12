#!/usr/bin/env python3
"""
PySpark Setup Test Script

Quick test to verify PySpark installation and basic functionality.
"""

import logging
import sys
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, count

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def test_spark_setup():
    """Test basic PySpark functionality."""
    logger.info("Testing PySpark setup...")
    
    try:
        # Initialize Spark session
        spark = SparkSession.builder \
            .appName("PySpark-Setup-Test") \
            .master("local[*]") \
            .config("spark.sql.adaptive.enabled", "true") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("WARN")
        logger.info("✅ Spark session created successfully")
        
        # Test basic DataFrame operations
        data = [
            ("Technology", "Apple Inc.", "AAPL"),
            ("Technology", "Microsoft Corp.", "MSFT"),
            ("Healthcare", "Johnson & Johnson", "JNJ"),
            ("Financials", "JPMorgan Chase", "JPM")
        ]
        
        columns = ["sector", "company", "ticker"]
        df = spark.createDataFrame(data, columns)
        
        logger.info("✅ DataFrame created successfully")
        
        # Test transformations
        sector_count = df.groupBy("sector").agg(count("*").alias("company_count"))
        
        logger.info("Sample data:")
        df.show()
        
        logger.info("Sector summary:")
        sector_count.show()
        
        # Test SQL operations
        df.createOrReplaceTempView("companies")
        sql_result = spark.sql("SELECT sector, COUNT(*) as count FROM companies GROUP BY sector")
        
        logger.info("SQL query result:")
        sql_result.show()
        
        logger.info("✅ All PySpark operations completed successfully")
        
        # Stop Spark session
        spark.stop()
        logger.info("✅ Spark session stopped")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ PySpark test failed: {e}")
        return False


def test_wikipedia_integration():
    """Test integration with existing Wikipedia client."""
    logger.info("Testing Wikipedia integration...")
    
    try:
        from etl_service.src.adapters.wiki_page_client import WikiPageClient
        
        wiki_client = WikiPageClient()
        companies_data = wiki_client.get_sp500_companies()
        
        logger.info(f"✅ Successfully fetched {len(companies_data)} companies from Wikipedia")
        
        # Test with Spark
        spark = SparkSession.builder \
            .appName("Wikipedia-Integration-Test") \
            .master("local[*]") \
            .getOrCreate()
        
        spark.sparkContext.setLogLevel("WARN")
        
        df = spark.createDataFrame(companies_data)
        logger.info(f"✅ Created Spark DataFrame with {df.count()} rows")
        
        # Show sample
        logger.info("Sample Wikipedia data:")
        df.select("Security", "Ticker", "GICS Sector").show(5)
        
        spark.stop()
        return True
        
    except Exception as e:
        logger.error(f"❌ Wikipedia integration test failed: {e}")
        return False


def main():
    """Run all tests."""
    logger.info("Starting PySpark setup verification...")
    
    tests = [
        ("Basic PySpark Setup", test_spark_setup),
        ("Wikipedia Integration", test_wikipedia_integration)
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"\n{'='*50}")
        logger.info(f"Running: {test_name}")
        logger.info(f"{'='*50}")
        
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info(f"\n{'='*50}")
    logger.info("TEST SUMMARY")
    logger.info(f"{'='*50}")
    
    passed = 0
    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        logger.info(f"{test_name}: {status}")
        if result:
            passed += 1
    
    logger.info(f"\nOverall: {passed}/{len(results)} tests passed")
    
    if passed == len(results):
        logger.info("🎉 All tests passed! PySpark setup is ready.")
        sys.exit(0)
    else:
        logger.error("❌ Some tests failed. Check the logs above.")
        sys.exit(1)


if __name__ == "__main__":
    main()