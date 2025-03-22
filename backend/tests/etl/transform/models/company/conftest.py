import pytest
from unittest.mock import MagicMock

@pytest.fixture
def mock_cursor():
    """Mock database cursor for testing."""
    cursor = MagicMock()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    return cursor

@pytest.fixture
def sample_company_data():
    """Sample company data for testing."""
    return {
        'id': 1,
        'name': 'Test Company',
        'ticker': 'TEST',
        'sub_industry_id': 1,
        'year_founded': 2000,
        'number_of_employees': 1000,
        'HQ_state': 'NY'
    }
