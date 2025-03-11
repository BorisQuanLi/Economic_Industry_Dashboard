import pytest
from unittest.mock import Mock, patch
from api.client import APIClient

class TestAPIClient(APIClient):
    def _get_secret(self):
        return "test_secret_key"

    def test_get_sectors(self):
        # ...existing code...
        pass

    def test_get_sector_metrics(self):
        # ...existing code...
        pass

    def test_store_raw_data(self):
        # ...existing code...
        pass

@pytest.fixture
def mock_boto3_session():
    with patch('boto3.Session') as mock_session:
        mock_session.return_value.client.return_value = Mock()
        yield mock_session

@pytest.fixture
def api_client(mock_boto3_session):
    return APIClient()

def test_get_sectors(api_client):
    sectors = api_client.get_sectors()
    assert isinstance(sectors, list)
    assert all(isinstance(sector, str) for sector in sectors)

def test_get_sector_metrics(api_client):
    metrics = api_client.get_sector_metrics("Technology")
    assert isinstance(metrics, dict)
    assert "growth" in metrics
    assert "revenue" in metrics

def test_store_raw_data(api_client, mock_boto3_session):
    test_data = {"test": "data"}
    api_client.store_raw_data(test_data, "test_dataset")
    mock_s3 = mock_boto3_session.return_value.client.return_value
    mock_s3.put_object.assert_called_once()
