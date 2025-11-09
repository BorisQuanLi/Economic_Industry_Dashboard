import pytest
from unittest.mock import MagicMock
from api.src.models.queries.query_company_price_pe_history import MixinCompanyPricePE
from api.src.models.quarterly_aggregation_models.aggregation_by_quarter import QuarterlyPricePE

class MockCompany(MixinCompanyPricePE):
    def __init__(self, name='Test Company'):
        self.name = name

    def __str__(self):
        return self.name

def test_get_all_company_names_in_sub_sector():
    """
    Test that get_all_company_names_in_sub_sector executes the correct SQL
    and returns a list of company names.
    """
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, 'Company A'),
        (2, 'Company B')
    ]
    
    mock_company = MockCompany()
    result = mock_company.get_all_company_names_in_sub_sector('Test Sub-Sector', mock_cursor)
    
    mock_cursor.execute.assert_called_once()
    assert result == ['Company A', 'Company B']

def test_create_price_pe_objs():
    """
    Test that the create_price_pe_objs method correctly
    creates a QuarterlyPricePE object from a record.
    """
    mock_company = MockCompany()
    record = (2022, 4, 150.0, 25.0)
    
    result_obj = mock_company.create_price_pe_objs(record)
    
    assert isinstance(result_obj, dict)
    assert result_obj['year'] == 2022
    assert result_obj['quarter'] == 4
    assert result_obj['closing_price'] == 150.0
    assert result_obj['price_earnings_ratio'] == 25.0

def test_to_quarterly_price_pe_json():
    """
    Test that to_quarterly_price_pe_json executes the correct SQL
    and returns a list of quarterly price/PE data.
    """
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, 2022, 4, 150.0, 25.0),
        (1, 2022, 3, 140.0, 23.0)
    ]
    
    mock_company = MockCompany()
    result = mock_company.to_quarterly_price_pe_json('Test Company', mock_cursor)
    
    mock_cursor.execute.assert_called_once()
    assert len(result) == 2
    assert result[0]['year'] == 2022
    assert result[1]['closing_price'] == 140.0
