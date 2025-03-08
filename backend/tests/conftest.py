import pytest
import pandas as pd
from unittest.mock import MagicMock
import sys
from pathlib import Path

# Add backend to Python path
backend_dir = Path(__file__).parent.parent
sys.path.append(str(backend_dir))

from api.src import create_app
from api.src.config import TestingConfig

@pytest.fixture
def app():
    """Create application for testing"""
    app = create_app(TestingConfig)
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
