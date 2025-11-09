import pytest
from unittest.mock import MagicMock
from api.src.models.queries.query_sector_quarterly_financials import MixinSectorQuarterlyFinancials
from api.src.models.quarterly_aggregation_models.aggregation_by_quarter import QuarterlyReportResult

class MockSubIndustry(MixinSectorQuarterlyFinancials):
    __table__ = 'sub_industries' # Assuming this mixin is used with SubIndustry
    def __init__(self, name='Test SubIndustry'):
        self.name = name

    def __str__(self):
        return self.name

def test_build_avg_quarterly_financials_obj():
    """
    Test that the build_avg_quarterly_financials_obj method correctly
    creates a QuarterlyReportResult object from a record.
    """
    mock_sub_industry = MockSubIndustry()
    record = (2022, 4, 100.0, 10.0, 1.0, 0.1)
    
    result_obj = mock_sub_industry.build_avg_quarterly_financials_obj(record, MagicMock())
    
    assert isinstance(result_obj, dict)
    assert result_obj['year'] == 2022
    assert result_obj['quarter'] == 4
    assert result_obj['revenue'] == 100.0
    assert result_obj['net_income'] == 10.0
    assert result_obj['earnings_per_share'] == 1.0
    assert result_obj['profit_margin'] == 0.1

def test_to_avg_quarterly_financials_json_by_sector():
    """
    Test that to_avg_quarterly_financials_json_by_sector executes the correct SQL
    and returns a list of quarterly average financial data.
    """
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, 2022, 4, 100.0, 10.0, 1.0, 0.1),
        (1, 2022, 3, 90.0, 9.0, 0.9, 0.09)
    ]
    
    mock_sub_industry = MockSubIndustry()
    result = mock_sub_industry.to_avg_quarterly_financials_json_by_sector('Technology', mock_cursor)
    
    mock_cursor.execute.assert_called_once()
    assert len(result) == 2
    assert result[0]['year'] == 2022
    assert result[1]['revenue'] == 90.0
