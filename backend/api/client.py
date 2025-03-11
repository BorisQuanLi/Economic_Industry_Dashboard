from pathlib import Path
import sys

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

import boto3
from botocore.exceptions import ClientError
import logging
import os
from typing import Dict, List, Any, Optional
import json

class APIClient:
    def __init__(self):
        self.session = boto3.Session(
            region_name=os.getenv('AWS_REGION', 'us-east-1')
        )
        self.s3 = self.session.client('s3')
        self.cloudwatch = self.session.client('cloudwatch')
        self.secrets = self.session.client('secretsmanager')
        self.logger = logging.getLogger(__name__)
        
        # Initialize with secrets
        try:
            self.db_credentials = self._get_secret('economic_dashboard_db')
        except Exception as e:
            self.logger.error(f"Failed to get DB credentials: {str(e)}")
            self.db_credentials = None

    def _get_secret(self, secret_name):
        """Get secret from AWS Secrets Manager"""
        try:
            response = self.secrets.get_secret_value(SecretId=secret_name)
            if 'SecretString' in response:
                return json.loads(response['SecretString'])
            return None
        except Exception as e:
            self.logger.error(f"Error getting secret {secret_name}: {str(e)}")
            return None

    def get_sectors(self):
        """Get list of all sectors"""
        try:
            # Implement actual sector retrieval logic
            return ["Technology", "Healthcare", "Finance"]
        except Exception as e:
            self.logger.error(f"Error getting sectors: {str(e)}")
            return []

    def get_sector_metrics(self, sector):
        """Get metrics for a specific sector"""
        try:
            # Implement actual metric retrieval logic
            return {"revenue": 1000000, "growth": 0.15}
        except Exception as e:
            self.logger.error(f"Error getting metrics for sector {sector}: {str(e)}")
            return {}

    def store_raw_data(self, data, dataset_name):
        """Store raw data in S3"""
        try:
            self.s3.put_object(
                Bucket='economic-dashboard',
                Key=f'raw/{dataset_name}.json',
                Body=json.dumps(data)
            )
            return True
        except Exception as e:
            self.logger.error(f"Error storing raw data: {str(e)}")
            return False
