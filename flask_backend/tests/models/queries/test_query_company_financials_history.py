import pytest
from unittest.mock import MagicMock
from api.src.models.queries.query_company_financials_history import MixinCompanyFinancials
from api.src.models.quarterly_aggregation_models.aggregation_by_quarter import QuarterlyReportResult

class MockCompany(MixinCompanyFinancials):
    def __init__(self, name='Test Company'):
        self.name = name

    def __str__(self):
        return self.name

def test_create_quarterly_financials_objs():
    """
    Test that the create_quarterly_financials_objs method correctly
    creates a QuarterlyReportResult object from a record.
    """
    mock_company = MockCompany()
    record = (2022, 4, 100.0, 10.0, 1.0, 0.1)
    
    result_obj = mock_company.create_quarterly_financials_objs(record)
    
    assert isinstance(result_obj, dict)
    assert result_obj['year'] == 2022
    assert result_obj['quarter'] == 4
    assert result_obj['revenue'] == 100.0
    assert result_obj['net_income'] == 10.0
    assert result_obj['earnings_per_share'] == 1.0
    assert result_obj['profit_margin'] == 0.1

def test_to_quarterly_financials_json():
    """
    Test that to_quarterly_financials_json executes the correct SQL
    and returns a list of quarterly financials.
    """
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, 2022, 4, 100.0, 10.0, 1.0, 0.1),
        (1, 2022, 3, 90.0, 9.0, 0.9, 0.09)
    ]
    
    mock_company = MockCompany()
    result = mock_company.to_quarterly_financials_json('Test Company', mock_cursor)
    
    mock_cursor.execute.assert_called_once()
    assert len(result) == 2
    assert result[0]['year'] == 2022
    assert result[1]['revenue'] == 90.0
