"""Tests for subindustry financial average models."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from backend.etl.transform.models.industry.subindustry_financial_average_model import SubIndustryFinancialAverage, SubIndustryQuarterlyAverage, SubIndustryQuarterlyAverageFinancials

@pytest.fixture
def mock_cursor():
    cursor = Mock()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    return cursor

@pytest.fixture
def sample_financial_data():
    return [
        {'quarter_label': '2023-Q1', 'quarter_date': datetime(2023, 3, 31), 
         'avg_revenue': 500000000, 'avg_net_income': 100000000, 
         'avg_eps': 2.0, 'avg_profit_margin': 20.0},
        {'quarter_label': '2022-Q4', 'quarter_date': datetime(2022, 12, 31), 
         'avg_revenue': 480000000, 'avg_net_income': 95000000, 
         'avg_eps': 1.9, 'avg_profit_margin': 19.8}
    ]

@pytest.fixture
def sample_pe_data():
    return [
        {'quarter_label': '2023-Q1', 'avg_pe_ratio': 22.5},
        {'quarter_label': '2022-Q4', 'avg_pe_ratio': 21.0}
    ]

@pytest.fixture
def sample_companies():
    return [
        {'id': 1, 'name': 'Company A', 'ticker': 'AAA'},
        {'id': 2, 'name': 'Company B', 'ticker': 'BBB'},
        {'id': 3, 'name': 'Company C', 'ticker': 'CCC'}
    ]

def test_subindustry_financial_average_creation():
    """Test creating a SubIndustryFinancialAverage instance."""
    subindustry_avg = SubIndustryFinancialAverage(
        sub_industry_id=1,
        sub_industry_name="Software",
        average_revenue=500000000,
        average_net_income=100000000,
        average_pe_ratio=22.5
    )
    
    assert subindustry_avg.sub_industry_id == 1
    assert subindustry_avg.sub_industry_name == "Software"
    assert subindustry_avg.average_revenue == 500000000
    assert subindustry_avg.average_net_income == 100000000
    assert subindustry_avg.average_pe_ratio == 22.5
    assert subindustry_avg.quarterly_averages is None

def test_get_sub_industry_averages(mock_cursor):
    """Test getting sub-industry averages for a metric."""
    mock_cursor.fetchall.return_value = [
        {'quarter': datetime(2023, 3, 31), 'avg_value': 500000000},
        {'quarter': datetime(2022, 12, 31), 'avg_value': 480000000}
    ]
    
    result = SubIndustryFinancialAverage.get_sub_industry_averages("Software", "revenue", mock_cursor)
    
    assert len(result) == 2
    assert result[str(datetime(2023, 3, 31))] == 500000000
    assert result[str(datetime(2022, 12, 31))] == 480000000
    mock_cursor.execute.assert_called_once()

def test_calculate_industry_concentration(mock_cursor):
    """Test calculating industry concentration (HHI)."""
    mock_cursor.fetchone.return_value = {'hhi': 2500.0}
    
    result = SubIndustryFinancialAverage.calculate_industry_concentration("Software", "revenue", mock_cursor)
    
    assert result == 2500.0
    mock_cursor.execute.assert_called_once()

def test_get_top_performers(mock_cursor):
    """Test getting top performers in a sub-industry."""
    mock_cursor.fetchall.return_value = [
        {'name': 'Company A', 'ticker': 'AAA', 'avg_value': 600000000},
        {'name': 'Company B', 'ticker': 'BBB', 'avg_value': 550000000}
    ]
    
    result = SubIndustryFinancialAverage.get_top_performers("Software", "revenue", mock_cursor, 2)
    
    assert len(result) == 2
    assert result[0]['name'] == 'Company A'
    assert result[0]['avg_value'] == 600000000
    mock_cursor.execute.assert_called_once()

def test_calculate_averages(mock_cursor):
    """Test calculating sub-industry financial averages."""
    # Mock get_sub_industry_name
    mock_cursor.fetchone.side_effect = [
        {'sub_industry_gics': 'Software'},  # First call to get sub-industry name
        None  # Placeholder for subsequent calls
    ]
    
    # Mock get_sub_industry_averages
    with patch.object(SubIndustryFinancialAverage, 'get_sub_industry_averages') as mock_get_averages:
        mock_get_averages.side_effect = [
            {str(datetime(2023, 3, 31)): 500000000, str(datetime(2022, 12, 31)): 480000000},  # revenue
            {str(datetime(2023, 3, 31)): 100000000, str(datetime(2022, 12, 31)): 95000000}    # net_income
        ]
        
        # Mock get_companies_in_sub_industry
        with patch('backend.etl.transform.models.company.company_info_model.CompanyInfo.get_companies_in_sub_industry') as mock_get_companies:
            mock_get_companies.return_value = [
                {'id': 1, 'name': 'Company A', 'ticker': 'AAA'},
                {'id': 2, 'name': 'Company B', 'ticker': 'BBB'}
            ]
            
            # Mock calculate_average_pe
            with patch('backend.etl.transform.models.company.company_price_earnings_model.PriceEarningsRatio.calculate_average_pe') as mock_calc_pe:
                mock_calc_pe.side_effect = [20.0, 25.0]
                
                result = SubIndustryFinancialAverage.calculate_averages(1, mock_cursor)
                
                assert result.sub_industry_id == 1
                assert result.sub_industry_name == 'Software'
                assert result.average_revenue == 500000000
                assert result.average_net_income == 100000000
                assert result.average_pe_ratio == 22.5  # (20.0 + 25.0) / 2

def test_get_formatted_quarterly_averages(mock_cursor, sample_financial_data, sample_pe_data):
    """Test getting formatted quarterly averages."""
    # Setup mocks
    mock_cursor.fetchall.side_effect = [sample_financial_data, sample_pe_data]
    
    result = SubIndustryFinancialAverage.get_formatted_quarterly_averages("Software", mock_cursor)
    
    assert len(result) == 2
    assert result[0].quarter == "2023-Q1"
    assert result[0].revenue == 500000000
    assert result[0].net_income == 100000000
    assert result[0].earnings_per_share == 2.0
    assert result[0].profit_margin == 20.0
    assert result[0].price_earnings_ratio == 22.5
    
    assert result[1].quarter == "2022-Q4"
    assert result[1].earnings_per_share == 1.9
    
    assert mock_cursor.execute.call_count == 2

def test_calculate_subindustry_average_quarterly_financials(mock_cursor, sample_financial_data, sample_pe_data, sample_companies):
    """Test calculating sub-industry average quarterly financials with history."""
    # Mock get_sub_industry_name
    mock_cursor.fetchone.side_effect = [
        {'sub_industry_gics': 'Software'},  # First call to get sub-industry name
        None  # Placeholder for subsequent calls
    ]
    
    # Mock get_sub_industry_averages
    with patch.object(SubIndustryFinancialAverage, 'get_sub_industry_averages') as mock_get_averages:
        mock_get_averages.side_effect = [
            {str(datetime(2023, 3, 31)): 500000000, str(datetime(2022, 12, 31)): 480000000},  # revenue
            {str(datetime(2023, 3, 31)): 100000000, str(datetime(2022, 12, 31)): 95000000}    # net_income
        ]
        
        # Mock get_companies_in_sub_industry
        with patch('backend.etl.transform.models.company.company_info_model.CompanyInfo.get_companies_in_sub_industry') as mock_get_companies:
            mock_get_companies.return_value = sample_companies
            
            # Mock calculate_average_pe
            with patch('backend.etl.transform.models.company.company_price_earnings_model.PriceEarningsRatio.calculate_average_pe') as mock_calc_pe:
                mock_calc_pe.side_effect = [20.0, 25.0, 23.0]
                
                # Mock get_formatted_quarterly_averages
                with patch.object(SubIndustryFinancialAverage, 'get_formatted_quarterly_averages') as mock_format:
                    q_avg1 = SubIndustryQuarterlyAverage(
                        quarter="2023-Q1",
                        revenue=500000000,
                        net_income=100000000,
                        earnings_per_share=2.0,
                        profit_margin=20.0,
                        price_earnings_ratio=22.5
                    )
                    q_avg2 = SubIndustryQuarterlyAverage(
                        quarter="2022-Q4", 
                        revenue=480000000,
                        net_income=95000000,
                        earnings_per_share=1.9,
                        profit_margin=19.8,
                        price_earnings_ratio=21.0
                    )
                    mock_format.return_value = [q_avg1, q_avg2]
                    
                    result = SubIndustryFinancialAverage.calculate_subindustry_average_quarterly_financials(1, mock_cursor)
                    
                    assert result.sub_industry_id == 1
                    assert result.sub_industry_name == 'Software'
                    assert result.average_revenue == 500000000
                    assert result.average_net_income == 100000000
                    assert result.average_pe_ratio == 22.666666666666668  # (20.0 + 25.0 + 23.0) / 3
                    
                    assert result.quarterly_averages is not None
                    assert len(result.quarterly_averages) == 2
                    assert result.quarterly_averages[0].quarter == "2023-Q1"
                    assert result.quarterly_averages[0].revenue == 500000000

def test_get_sub_industry_averages_no_data(mock_cursor):
    """Test getting sub-industry averages when no data exists."""
    mock_cursor.fetchall.return_value = []
    result = SubIndustryQuarterlyAverageFinancials.get_sub_industry_averages(
        "NonExistentIndustry", "revenue", mock_cursor)
    assert result == {}

def test_calculate_industry_concentration_no_data(mock_cursor):
    """Test concentration calculation when no data exists."""
    mock_cursor.fetchone.return_value = None
    result = SubIndustryQuarterlyAverageFinancials.calculate_industry_concentration(
        "NonExistentIndustry", "revenue", mock_cursor)
    assert result is None

def test_get_formatted_quarterly_averages_no_financial_data(mock_cursor):
    """Test getting formatted averages when no financial data exists."""
    mock_cursor.fetchall.side_effect = [[], []]  # No financial data, no PE data
    result = SubIndustryQuarterlyAverageFinancials.get_formatted_quarterly_averages(
        "Software", mock_cursor)
    assert result == []
