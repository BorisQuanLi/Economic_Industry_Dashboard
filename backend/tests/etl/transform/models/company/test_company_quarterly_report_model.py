import pytest
from etl.transform.models.company.company_quarterly_report_model import CompanyQuarterlyReport

@pytest.fixture
def sample_quarterly_data():
    return {
        'id': 1,
        'date': '2023-01-01',
        'company_id': 1,
        'revenue': 1000000.0,
        'net_income': 100000.0,
        'earnings_per_share': 2.5,
        'profit_margin': 0.1
    }

def test_quarterly_report_creation(sample_quarterly_data):
    """Test CompanyQuarterlyReport instance creation."""
    report = CompanyQuarterlyReport(**sample_quarterly_data)
    assert report.revenue == 1000000.0
    assert report.net_income == 100000.0

def test_calculate_growth_rate(mock_cursor):
    """Test quarterly growth rate calculation."""
    mock_cursor.fetchone.return_value = {'growth_rate': 10.5}
    growth_rate = CompanyQuarterlyReport.calculate_growth_rate(1, 'revenue', mock_cursor)
    assert growth_rate == 10.5
