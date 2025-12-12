"""
AWS Glue Job for S&P 500 ETL Pipeline

This script is designed to run as an AWS Glue job, processing S&P 500 company data
using Glue's managed Spark environment.

Key Features:
- Serverless execution on AWS Glue
- Automatic scaling based on data volume
- Integration with AWS services (S3, RDS, etc.)
- Built-in monitoring and logging
"""

import sys
import logging
from datetime import datetime

from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, when, split, current_timestamp, lit

# Initialize Glue context
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)

# Set up logging
logger = glueContext.get_logger()
logger.info("Starting AWS Glue S&P 500 ETL Job")

# Get job parameters
args = getResolvedOptions(sys.argv, [
    'JOB_NAME',
    'S3_BUCKET',
    'DATABASE_CONNECTION',
    'OUTPUT_TABLE'
])

job.init(args['JOB_NAME'], args)


class GlueS3ETLPipeline:
    """AWS Glue ETL Pipeline for S&P 500 data processing."""
    
    def __init__(self, glue_context, spark_session):
        self.glue_context = glue_context
        self.spark = spark_session
        self.s3_bucket = args['S3_BUCKET']
        self.db_connection = args['DATABASE_CONNECTION']
        self.output_table = args['OUTPUT_TABLE']
    
    def extract_from_s3(self, s3_path: str):
        """Extract data from S3 using Glue Data Catalog."""
        logger.info(f"Extracting data from S3: {s3_path}")
        
        try:
            # Create DynamicFrame from S3
            dynamic_frame = self.glue_context.create_dynamic_frame.from_options(
                format_options={"multiline": False},
                connection_type="s3",
                format="json",
                connection_options={
                    "paths": [s3_path],
                    "recurse": True
                },
                transformation_ctx="s3_source"
            )
            
            logger.info(f"Successfully extracted {dynamic_frame.count()} records from S3")
            return dynamic_frame
            
        except Exception as e:
            logger.error(f"Failed to extract from S3: {e}")
            raise
    
    def transform_companies_data(self, dynamic_frame):
        """Transform companies data using Glue transformations."""
        logger.info("Transforming companies data with AWS Glue...")
        
        try:
            # Convert to DataFrame for complex transformations
            df = dynamic_frame.toDF()
            
            # Apply transformations
            transformed_df = df.select(
                col("Security").alias("name"),
                col("Ticker").alias("ticker"),
                col("GICS Sector").alias("sector"),
                col("GICS Sub-Industry").alias("sub_industry"),
                col("Headquarters Location").alias("headquarters")
            ).withColumn(
                "hq_state",
                when(col("headquarters").contains(", "), 
                     split(col("headquarters"), ", ").getItem(1))
                .otherwise(col("headquarters"))
            ).withColumn(
                "processed_timestamp",
                current_timestamp()
            ).withColumn(
                "job_run_id",
                lit(args['JOB_RUN_ID'] if 'JOB_RUN_ID' in args else 'manual')
            )
            
            # Convert back to DynamicFrame
            transformed_dynamic_frame = DynamicFrame.fromDF(
                transformed_df, 
                self.glue_context, 
                "transformed_companies"
            )
            
            logger.info("Data transformation completed")
            return transformed_dynamic_frame
            
        except Exception as e:
            logger.error(f"Failed to transform data: {e}")
            raise
    
    def load_to_rds(self, dynamic_frame):
        """Load data to RDS PostgreSQL using Glue connection."""
        logger.info(f"Loading data to RDS table: {self.output_table}")
        
        try:
            # Write to RDS using Glue connection
            self.glue_context.write_dynamic_frame.from_jdbc_conf(
                frame=dynamic_frame,
                catalog_connection=self.db_connection,
                connection_options={
                    "dbtable": self.output_table,
                    "database": "postgres"
                },
                transformation_ctx="rds_sink"
            )
            
            logger.info(f"Successfully loaded data to RDS table: {self.output_table}")
            
        except Exception as e:
            logger.error(f"Failed to load to RDS: {e}")
            raise
    
    def write_to_s3_parquet(self, dynamic_frame, output_path: str):
        """Write processed data to S3 in Parquet format."""
        logger.info(f"Writing processed data to S3: {output_path}")
        
        try:
            self.glue_context.write_dynamic_frame.from_options(
                frame=dynamic_frame,
                connection_type="s3",
                format="glueparquet",
                connection_options={
                    "path": output_path,
                    "partitionKeys": ["sector"]
                },
                format_options={
                    "compression": "snappy"
                },
                transformation_ctx="s3_parquet_sink"
            )
            
            logger.info("Successfully wrote data to S3 in Parquet format")
            
        except Exception as e:
            logger.error(f"Failed to write to S3: {e}")
            raise
    
    def run_data_quality_checks(self, dynamic_frame):
        """Run data quality checks using Glue Data Quality."""
        logger.info("Running data quality checks...")
        
        try:
            df = dynamic_frame.toDF()
            
            # Basic quality metrics
            total_records = df.count()
            null_tickers = df.filter(col("ticker").isNull()).count()
            null_names = df.filter(col("name").isNull()).count()
            
            # Log quality metrics
            logger.info(f"Data Quality Report:")
            logger.info(f"  Total records: {total_records}")
            logger.info(f"  Null tickers: {null_tickers}")
            logger.info(f"  Null names: {null_names}")
            logger.info(f"  Data quality score: {((total_records - null_tickers - null_names) / total_records * 100):.2f}%")
            
            # Fail job if data quality is too poor
            if null_tickers > total_records * 0.1:  # More than 10% null tickers
                raise ValueError(f"Data quality check failed: {null_tickers} null tickers out of {total_records} records")
            
        except Exception as e:
            logger.error(f"Data quality check failed: {e}")
            raise
    
    def run(self):
        """Run the complete Glue ETL pipeline."""
        logger.info("Starting AWS Glue ETL pipeline execution...")
        
        try:
            # Extract
            input_path = f"s3://{self.s3_bucket}/raw/sp500_companies/"
            raw_data = self.extract_from_s3(input_path)
            
            # Transform
            transformed_data = self.transform_companies_data(raw_data)
            
            # Data Quality
            self.run_data_quality_checks(transformed_data)
            
            # Load to RDS
            self.load_to_rds(transformed_data)
            
            # Also save to S3 for analytics
            output_path = f"s3://{self.s3_bucket}/processed/sp500_companies/"
            self.write_to_s3_parquet(transformed_data, output_path)
            
            logger.info("AWS Glue ETL pipeline completed successfully")
            
        except Exception as e:
            logger.error(f"AWS Glue ETL pipeline failed: {e}")
            raise


def main():
    """Main execution function for AWS Glue job."""
    try:
        # Initialize pipeline
        pipeline = GlueS3ETLPipeline(glueContext, spark)
        
        # Run pipeline
        pipeline.run()
        
        # Commit job
        job.commit()
        
        logger.info("AWS Glue job completed successfully")
        
    except Exception as e:
        logger.error(f"AWS Glue job failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()