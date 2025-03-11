import pytest
from unittest.mock import MagicMock
import pandas as pd

class MockContainer:
    def __init__(self):
        self.items = []
    
    def metric(self, label, value):
        self.items.append({"label": label, "value": value})

@pytest.fixture
def streamlit_test_container():
    return MockContainer()

@pytest.fixture
def mock_api_client():
    client = MagicMock()
    client.get_sector_metrics.return_value = {
        "average_revenue": 1000,
        "average_profit": 500,
        "total_market_cap": 10000
    }
    client.get_sector_companies = MagicMock()
    return client

@pytest.fixture
def mock_error_api_client():
    client = MagicMock()
    client.get_sector_metrics.side_effect = Exception("API Error")
    return client

@pytest.fixture
def mock_sector_companies():
    return pd.DataFrame({
        "company_name": ["CompanyA", "CompanyB", "CompanyC"],
        "revenue": [1000, 2000, 3000],
        "profit_margin": [10.5, 15.2, 8.7],
        "market_cap": [5000, 7000, 4000]
    })
