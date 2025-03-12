import pytest
from repositories.local import LocalPostgresRepository

class TestLocalPostgresRepository:
    def test_get_sectors(self, test_db_connection_params):
        repo = LocalPostgresRepository(test_db_connection_params)
        sectors = repo.get_sectors()
        assert isinstance(sectors, list)
        assert all(isinstance(sector, str) for sector in sectors)

    def test_get_sector_metrics(self, test_db_connection_params):
        repo = LocalPostgresRepository(test_db_connection_params)
        metrics = repo.get_sector_metrics("Tech")
        assert isinstance(metrics, dict)
        assert "revenue" in metrics
        assert "growth" in metrics

    def test_store_raw_data(self, test_db_connection_params):
        repo = LocalPostgresRepository(test_db_connection_params)
        test_data = {"test": "data"}
        result = repo.store_raw_data(test_data, "test_dataset")
        assert result is True
