import os
import sys
from pathlib import Path
import pytest
import pandas as pd
from unittest.mock import MagicMock

# Setup proper Python path for imports
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
project_root = os.path.abspath(os.path.join(backend_dir, '..'))

# Ensure both paths are in sys.path
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Project imports
from backend.webservice.factory import create_app
from backend.etl.load.data_persistence.local_postgres import LocalPostgresRepository
from backend.etl.load.data_persistence.aws import AWSRepository

# Define mock classes if needed
class MockLocalPostgresRepository:
    pass

class MockAWSRepository:
    pass

class MockIndustryAnalyzer:
    pass

@pytest.fixture
def mock_local_repository():
    """Mock local PostgreSQL repository"""
    repo = MagicMock(spec=MockLocalPostgresRepository)
    repo.get_sectors.return_value = ["Tech", "Healthcare", "Finance"]
    repo.get_sector_metrics.return_value = {"revenue": 1000000, "growth": 0.15}
    repo.store_raw_data.return_value = True
    return repo

@pytest.fixture
def mock_aws_repository():
    """Mock AWS repository"""
    repo = MagicMock(spec=MockAWSRepository)
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
    app = create_app()
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
    monkeypatch.setattr('etl.load.db.connection.get_db_connection', mock_get_db)
    return mock

@pytest.fixture
def sample_company_data():
    return pd.DataFrame({
        'company_name': ['A', 'B', 'C'],
        'sector': ['Tech', 'Tech', 'Tech'],
        'revenue': [100, 200, 300],
        'profit': [10, 20, 30],
        'market_cap': [1000, 2000, 300]
    })

@pytest.fixture
def mock_db_cursor():
    """Mock database cursor for model tests."""
    cursor = MagicMock()
    cursor.fetchall.return_value = []
    cursor.fetchone.return_value = None
    return cursor

@pytest.fixture
def sample_sector_data():
    """Sample sector data for tests."""
    return {
        'sector_gics': 'TEST001',
        'sector_name': 'Test Sector',
        'description': 'Test sector description'
    }