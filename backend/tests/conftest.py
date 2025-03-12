import pytest
import pandas as pd
from unittest.mock import MagicMock
from app import create_app
from repositories.local import LocalPostgresRepository
from repositories.cloud import AWSRepository
from api.src import create_app as api_create_app
from api.src.config import TestingConfig

# Existing fixtures...

@pytest.fixture
def mock_local_repository():
    """Mock local PostgreSQL repository"""
    repo = MagicMock(spec=LocalPostgresRepository)
    repo.get_sectors.return_value = ["Tech", "Healthcare", "Finance"]
    repo.get_sector_metrics.return_value = {"revenue": 1000000, "growth": 0.15}
    repo.store_raw_data.return_value = True
    return repo

@pytest.fixture
def mock_aws_repository():
    """Mock AWS repository"""
    repo = MagicMock(spec=AWSRepository)
    repo.get_sectors.return_value = ["Tech", "Healthcare", "Finance"]
    repo.get_sector_metrics.return_value = {"revenue": 1000000, "growth": 0.15}
    repo.store_raw_data.return_value = True
    return repo

@pytest.fixture
def test_db_connection_params():
    """Test database connection parameters"""
    return {
        'dbname': 'test_economic_dashboard',
        'user': 'postgres',
        'password': 'test_password',
        'host': 'localhost'
    }

@pytest.fixture
def app():
    """Create application for testing"""
    app = api_create_app(TestingConfig)
    app.config['DATABASE'] = 'postgresql://postgres:postgres@localhost:5432/test_db'
    return app

@pytest.fixture
def client(app):
    """Create test client"""
    return app.test_client()

@pytest.fixture
def mock_db(monkeypatch):
    """Mock database connection"""
    mock = MagicMock()
    def mock_get_db():
        return mock
    monkeypatch.setattr('api.src.db.db.get_db_connection', mock_get_db)
    return mock

@pytest.fixture
def sample_company_data():
    return pd.DataFrame({
        'company_name': ['A', 'B', 'C'],
        'sector': ['Tech', 'Tech', 'Tech'],
        'revenue': [100, 200, 300],
        'profit': [10, 20, 30],
        'market_cap': [1000, 2000, 3000]
    })