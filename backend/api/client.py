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
        self.db_credentials = self._get_secret('economic_dashboard_db')

    # ...rest of the APIClient implementation...
