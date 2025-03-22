from unittest.mock import Mock
import pytest
from backend.etl.transform.models.company.company_price_earnings_model import PriceEarningsRatio

@pytest.fixture
def mock_cursor():
    return Mock()

@pytest.fixture
def sample_pe_data():
    return {
        'id': 1,
        'date': '2023-01-01',
        'company_id': 1,
        'closing_price': 100.0,
        'price_earnings_ratio': 15.5
    }

def test_find_by_company_id(mock_cursor, sample_pe_data):
    mock_cursor.fetchall.return_value = [sample_pe_data]
    result = PriceEarningsRatio.find_by_company_id(1, mock_cursor)
    assert len(result) == 1
    assert result[0].price_earnings_ratio == 15.5

def test_calculate_average_pe(mock_cursor):
    mock_cursor.fetchone.return_value = {'avg_pe': 16.5}
    result = PriceEarningsRatio.calculate_average_pe(1, mock_cursor)
    assert result == 16.5

def test_get_pe_percentile(mock_cursor):
    mock_cursor.fetchone.return_value = {'percentile': 75.5}
    result = PriceEarningsRatio.get_pe_percentile(1, mock_cursor)
    assert result == 75.5
