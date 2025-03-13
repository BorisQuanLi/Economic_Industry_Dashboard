import os
from typing import Dict, List, Any
from ..repositories.base import DataRepository
from ..repositories.local_postgres import LocalPostgresRepository
from ..repositories.aws import AWSRepository

class APIClient:
    def __init__(self):
        self.repository = self._get_repository()
        
    def _get_repository(self) -> DataRepository:
        env = os.getenv('APP_ENV', 'local')
        
        if env == 'local':
            connection_params = {
                'dbname': 'economic_dashboard',
                'user': 'postgres',
                'password': 'your_password',
                'host': 'localhost'
            }
            return LocalPostgresRepository(connection_params)
        else:
            return AWSRepository()

    def get_sectors(self) -> List[str]:
        return self.repository.get_sectors()

    def get_sector_metrics(self, sector: str) -> Dict[str, Any]:
        return self.repository.get_sector_metrics(sector)

    def store_raw_data(self, data: Dict[str, Any], dataset_name: str) -> bool:
        return self.repository.store_raw_data(data, dataset_name)
