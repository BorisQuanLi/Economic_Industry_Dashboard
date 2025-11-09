import pytest
from unittest.mock import MagicMock
from api.src.models.queries.query_sub_sector_quarterly_financials import MixinSubSectorQuarterlyFinancials
from api.src.models.quarterly_aggregation_models.aggregation_by_quarter import QuarterlyReportResult

class MockSubIndustry(MixinSubSectorQuarterlyFinancials):
    __table__ = 'sub_industries'
    def __init__(self, name='Test SubIndustry'):
        self.name = name

    def __str__(self):
        return self.name

def test_create_avg_quarterly_financialsobjs():
    """
    Test that the create_avg_quarterly_financialsobjs method correctly
    creates a QuarterlyReportResult object from a record.
    """
    mock_sub_industry = MockSubIndustry()
    record = (2022, 4, 100.0, 10.0, 1.0, 0.1)
    
    result_obj = mock_sub_industry.create_avg_quarterly_financialsobjs(record)
    
    assert isinstance(result_obj, dict)
    assert result_obj['year'] == 2022
    assert result_obj['quarter'] == 4
    assert result_obj['revenue'] == 100.0
    assert result_obj['net_income'] == 10.0
    assert result_obj['earnings_per_share'] == 1.0
    assert result_obj['profit_margin'] == 0.1

def test_to_sub_industry_avg_quarterly_financials_json():
    """
    Test that to_sub_industry_avg_quarterly_financials_json executes the correct SQL
    and returns a list of quarterly average financial data.
    """
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, 2022, 4, 100.0, 10.0, 1.0, 0.1),
        (1, 2022, 3, 90.0, 9.0, 0.9, 0.09)
    ]
    
    mock_sub_industry = MockSubIndustry()
    result = mock_sub_industry.to_sub_industry_avg_quarterly_financials_json('Test Sub-Industry', mock_cursor)
    
    mock_cursor.execute.assert_called_once()
    assert len(result) == 2
    assert result[0]['year'] == 2022
    assert result[1]['revenue'] == 90.0
