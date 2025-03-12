import pytest
from unittest.mock import patch
from api.client import APIClient

@pytest.fixture
def mock_aws_repository():
    with patch('api.client.AWSRepository') as MockRepo:
        repo = MockRepo.return_value
        repo.get_sectors.return_value = ["Tech", "Healthcare", "Finance"]
        repo.get_sector_metrics.return_value = {"revenue": 1000000, "growth": 0.15}
        repo.store_raw_data.return_value = True
        yield repo

def test_get_sectors(mock_aws_repository):
    client = APIClient()
    sectors = client.get_sectors()
    assert sectors == ["Tech", "Healthcare", "Finance"]

def test_get_sector_metrics(mock_aws_repository):
    client = APIClient()
    metrics = client.get_sector_metrics("Tech")
    assert metrics == {"revenue": 1000000, "growth": 0.15}

def test_store_raw_data(mock_aws_repository):
    client = APIClient()
    result = client.store_raw_data({"data": "sample"}, "dataset_name")
    assert result is True