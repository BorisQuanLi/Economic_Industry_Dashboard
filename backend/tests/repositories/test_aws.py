import pytest
from unittest.mock import patch
from repositories.cloud import AWSRepository

class TestAWSRepository:
    @patch('boto3.client')
    def test_get_sectors(self, mock_boto3):
        repo = AWSRepository()
        sectors = repo.get_sectors()
        assert isinstance(sectors, list)
        assert all(isinstance(sector, str) for sector in sectors)

    @patch('boto3.client')
    def test_get_sector_metrics(self, mock_boto3):
        repo = AWSRepository()
        metrics = repo.get_sector_metrics("Tech")
        assert isinstance(metrics, dict)
        assert "revenue" in metrics
        assert "growth" in metrics

    @patch('boto3.client')
    def test_store_raw_data(self, mock_boto3):
        repo = AWSRepository()
        test_data = {"test": "data"}
        result = repo.store_raw_data(test_data, "test_dataset")
        assert result is True
