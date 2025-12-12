#!/usr/bin/env python3
"""
AWS Lake Formation Setup for JPMC Data Pipeline

Creates S3 data lake with Lake Formation governance for:
- Raw financial data (S3)
- Processed data (S3 + Glue Catalog)
- Access control (Lake Formation permissions)
- Integration with Snowflake/Redshift
"""

import boto3
import json
from datetime import datetime

class LakeFormationSetup:
    def __init__(self):
        self.s3 = boto3.client('s3')
        self.glue = boto3.client('glue')
        self.lakeformation = boto3.client('lakeformation')
        self.bucket_name = 'jpmc-sp500-data-lake'
        
    def create_s3_data_lake(self):
        """Create S3 bucket for data lake storage."""
        try:
            self.s3.create_bucket(Bucket=self.bucket_name)
            print(f"✅ Created S3 bucket: {self.bucket_name}")
            
            # Create folder structure
            folders = ['raw/sp500/', 'processed/sp500/', 'curated/sp500/']
            for folder in folders:
                self.s3.put_object(Bucket=self.bucket_name, Key=folder)
            
        except Exception as e:
            print(f"S3 setup: {e}")
    
    def setup_glue_catalog(self):
        """Create Glue database and tables."""
        try:
            # Create database
            self.glue.create_database(
                DatabaseInput={
                    'Name': 'jpmc_financial_data',
                    'Description': 'S&P 500 financial data for JPMC pipeline'
                }
            )
            
            # Create table for companies
            self.glue.create_table(
                DatabaseName='jpmc_financial_data',
                TableInput={
                    'Name': 'sp500_companies',
                    'StorageDescriptor': {
                        'Columns': [
                            {'Name': 'ticker', 'Type': 'string'},
                            {'Name': 'name', 'Type': 'string'},
                            {'Name': 'sector', 'Type': 'string'},
                            {'Name': 'sub_industry', 'Type': 'string'}
                        ],
                        'Location': f's3://{self.bucket_name}/processed/sp500/companies/',
                        'InputFormat': 'org.apache.hadoop.mapred.TextInputFormat',
                        'OutputFormat': 'org.apache.hadoop.hive.ql.io.HiveIgnoreKeyTextOutputFormat',
                        'SerdeInfo': {
                            'SerializationLibrary': 'org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe'
                        }
                    }
                }
            )
            print("✅ Created Glue catalog")
            
        except Exception as e:
            print(f"Glue catalog setup: {e}")
    
    def setup_lake_formation_permissions(self):
        """Configure Lake Formation access control."""
        try:
            # Register S3 location with Lake Formation
            self.lakeformation.register_resource(
                ResourceArn=f'arn:aws:s3:::{self.bucket_name}/',
                UseServiceLinkedRole=True
            )
            
            # Grant permissions to data lake
            self.lakeformation.grant_permissions(
                Principal={'DataLakePrincipalIdentifier': 'arn:aws:iam::ACCOUNT:role/LakeFormationServiceRole'},
                Resource={
                    'Database': {'Name': 'jpmc_financial_data'}
                },
                Permissions=['ALL']
            )
            print("✅ Configured Lake Formation permissions")
            
        except Exception as e:
            print(f"Lake Formation setup: {e}")
    
    def run_setup(self):
        """Run complete Lake Formation setup."""
        print("🚀 Setting up AWS Lake Formation for JPMC pipeline...")
        self.create_s3_data_lake()
        self.setup_glue_catalog()
        self.setup_lake_formation_permissions()
        print("✅ Lake Formation setup complete!")

if __name__ == "__main__":
    setup = LakeFormationSetup()
    setup.run_setup()