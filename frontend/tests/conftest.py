import pytest
from unittest.mock import MagicMock
import pandas as pd
from api.client import APIClient

@pytest.fixture
def mock_api_client():
    """Provide a mocked API client for testing"""
    client = MagicMock(spec=APIClient)
    client.get_sectors.return_value = ['Technology', 'Healthcare', 'Finance']
    client.get_sector_metrics.return_value = {
        'avg_revenue': 1000,
        'avg_profit_margin': 15.5,
        'total_market_cap': 500
    }
    return client

@pytest.fixture
def sample_performance_data():
    """Provide sample time series data for testing"""
    return pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=4, freq='Q'),
        'value': [100, 110, 120, 115]
    })

@pytest.fixture
def streamlit_test_container():
    """Mock Streamlit container for testing UI components"""
    class MockContainer:
        def __init__(self):
            self.items = []
        
        def metric(self, label, value):
            self.items.append({'label': label, 'value': value})
    
    return MockContainer()

@pytest.fixture
def mock_sector_companies():
    """Provide sample company data for a sector"""
    return pd.DataFrame({
        'company_name': ['CompanyA', 'CompanyB', 'CompanyC'],
        'revenue': [1000, 2000, 3000],
        'profit_margin': [10.5, 15.2, 8.7],
        'market_cap': [5000, 7000, 4000]
    })

@pytest.fixture
def mock_error_api_client():
    """Provide a mocked API client that simulates errors"""
    client = MagicMock(spec=APIClient)
    client.get_sectors.side_effect = Exception("API Error")
    client.get_sector_metrics.side_effect = Exception("API Error")
    return client
