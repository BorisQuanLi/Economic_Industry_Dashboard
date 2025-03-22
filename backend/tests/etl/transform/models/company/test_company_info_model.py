import pytest
from etl.transform.models.company.company_info_model import CompanyInfo

def test_company_info_creation(sample_company_data):
    """Test CompanyInfo instance creation."""
    company = CompanyInfo(**sample_company_data)
    assert company.id == 1
    assert company.ticker == 'TEST'
    assert company.name == 'Test Company'

def test_find_by_stock_ticker(mock_cursor):
    """Test finding company by stock ticker."""
    mock_cursor.fetchone.return_value = {
        'id': 1, 'ticker': 'TEST', 'name': 'Test Company',
        'sub_industry_id': 1, 'year_founded': 2000,
        'number_of_employees': 1000, 'HQ_state': 'NY'
    }
    company = CompanyInfo.find_by_stock_ticker('TEST', mock_cursor)
    assert company.ticker == 'TEST'
    mock_cursor.execute.assert_called_once()

def test_find_by_company_id(mock_cursor):
    """Test finding company by ID."""
    mock_cursor.fetchone.return_value = {
        'id': 1, 'ticker': 'TEST', 'name': 'Test Company',
        'sub_industry_id': 1, 'year_founded': 2000,
        'number_of_employees': 1000, 'HQ_state': 'NY'
    }
    company = CompanyInfo.find_by_company_id(1, mock_cursor)
    assert company.id == 1
    mock_cursor.execute.assert_called_once()

def test_invalid_attribute(sample_company_data):
    """Test creating CompanyInfo with invalid attribute."""
    with pytest.raises(TypeError):
        CompanyInfo(invalid_field="test", **sample_company_data)
