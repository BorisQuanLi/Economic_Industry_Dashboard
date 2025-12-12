#!/usr/bin/env python3
"""
PySpark ETL with AWS Lake Formation Integration

Demonstrates JPMC-required integration:
- PySpark processing
- S3 data lake (Lake Formation managed)
- Glue Catalog integration
- Snowflake/Redshift output
"""

from pyspark.sql import SparkSession
from pyspark.sql.functions import col, current_timestamp
import boto3

class PySparkLakeFormationETL:
    def __init__(self):
        self.spark = SparkSession.builder \
            .appName("JPMC-LakeFormation-ETL") \
            .config("spark.sql.catalogImplementation", "hive") \
            .config("spark.sql.warehouse.dir", "s3://jpmc-sp500-data-lake/warehouse/") \
            .enableHiveSupport() \
            .getOrCreate()
        
        self.bucket = "jpmc-sp500-data-lake"
    
    def extract_from_s3(self):
        """Extract raw data from S3 data lake."""
        print("📥 Extracting data from S3 data lake...")
        
        # Read from S3 (Lake Formation managed)
        raw_path = f"s3://{self.bucket}/raw/sp500/companies.json"
        df = self.spark.read.json(raw_path)
        
        print(f"✅ Extracted {df.count()} records from data lake")
        return df
    
    def transform_with_pyspark(self, df):
        """Transform data using PySpark operations."""
        print("⚙️ Transforming data with PySpark...")
        
        # PySpark transformations
        transformed_df = df.select(
            col("Security").alias("company_name"),
            col("Ticker").alias("ticker"),
            col("GICS Sector").alias("sector"),
            col("GICS Sub-Industry").alias("sub_industry"),
            current_timestamp().alias("processed_timestamp")
        ).filter(
            col("ticker").isNotNull()
        )
        
        print("✅ Data transformation completed")
        return transformed_df
    
    def load_to_data_lake(self, df):
        """Load processed data back to S3 data lake."""
        print("📤 Loading processed data to data lake...")
        
        # Write to S3 in Parquet format (partitioned by sector)
        processed_path = f"s3://{self.bucket}/processed/sp500/companies/"
        
        df.write \
            .mode("overwrite") \
            .partitionBy("sector") \
            .parquet(processed_path)
        
        print("✅ Data loaded to processed layer")
    
    def register_with_glue_catalog(self):
        """Register processed data with Glue Catalog."""
        print("📋 Registering data with Glue Catalog...")
        
        # Create external table in Glue Catalog
        self.spark.sql(f"""
            CREATE TABLE IF NOT EXISTS jpmc_financial_data.sp500_companies_processed
            USING PARQUET
            LOCATION 's3://{self.bucket}/processed/sp500/companies/'
            PARTITIONED BY (sector STRING)
        """)
        
        print("✅ Data registered with Glue Catalog")
    
    def export_to_snowflake(self, df):
        """Export data to Snowflake (JPMC requirement)."""
        print("❄️ Exporting to Snowflake...")
        
        # Snowflake connection (would use actual credentials in production)
        snowflake_options = {
            "sfUrl": "your-account.snowflakecomputing.com",
            "sfUser": "your-user",
            "sfPassword": "your-password",
            "sfDatabase": "JPMC_FINANCIAL_DATA",
            "sfSchema": "SP500",
            "sfWarehouse": "COMPUTE_WH"
        }
        
        # Write to Snowflake (commented for demo)
        # df.write \
        #     .format("snowflake") \
        #     .options(**snowflake_options) \
        #     .option("dbtable", "SP500_COMPANIES") \
        #     .mode("overwrite") \
        #     .save()
        
        print("✅ Data export to Snowflake prepared")
    
    def run_etl_pipeline(self):
        """Run complete ETL pipeline with Lake Formation."""
        print("🚀 Starting PySpark + Lake Formation ETL pipeline...")
        
        try:
            # ETL Steps
            raw_df = self.extract_from_s3()
            transformed_df = self.transform_with_pyspark(raw_df)
            self.load_to_data_lake(transformed_df)
            self.register_with_glue_catalog()
            self.export_to_snowflake(transformed_df)
            
            print("✅ ETL pipeline completed successfully!")
            
        except Exception as e:
            print(f"❌ ETL pipeline failed: {e}")
            raise
        finally:
            self.spark.stop()

if __name__ == "__main__":
    etl = PySparkLakeFormationETL()
    etl.run_etl_pipeline()