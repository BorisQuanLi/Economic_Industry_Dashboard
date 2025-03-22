"""Tests for sector financial average models."""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from backend.etl.transform.models.industry.sector_financial_average_model import SectorFinancialAverage, SectorQuarterlyAverage, SectorQuarterlyAverageFinancials
from backend.etl.transform.models.industry.subindustry_model import SubIndustry

@pytest.fixture
def mock_cursor():
    cursor = Mock()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    return cursor

@pytest.fixture
def sample_sub_industries():
    return [
        SubIndustry(id=1, sub_industry_gics="Software", sector_id=1, sector_gics="Information Technology"),
        SubIndustry(id=2, sub_industry_gics="Hardware", sector_id=1, sector_gics="Information Technology")
    ]

@pytest.fixture
def sample_financial_data():
    return [
        {'quarter_label': '2023-Q1', 'quarter_date': datetime(2023, 3, 31), 
         'avg_revenue': 1000000000, 'avg_net_income': 200000000, 
         'avg_eps': 2.5, 'avg_profit_margin': 20.0},
        {'quarter_label': '2022-Q4', 'quarter_date': datetime(2022, 12, 31), 
         'avg_revenue': 950000000, 'avg_net_income': 190000000, 
         'avg_eps': 2.4, 'avg_profit_margin': 19.5}
    ]

@pytest.fixture
def sample_pe_data():
    return [
        {'quarter_label': '2023-Q1', 'avg_pe_ratio': 25.5},
        {'quarter_label': '2022-Q4', 'avg_pe_ratio': 24.0}
    ]

def test_sector_financial_average_creation(sample_sub_industries):
    """Test creating a SectorFinancialAverage instance."""
    sector_avg = SectorFinancialAverage("Information Technology", sample_sub_industries)
    assert sector_avg.sector_name == "Information Technology"
    assert len(sector_avg.sub_industries) == 2
    assert sector_avg.quarterly_averages is None

def test_from_sector(mock_cursor, sample_sub_industries):
    """Test creating a SectorFinancialAverage from sector name."""
    mock_cursor.fetchall.return_value = [
        {'id': 1, 'sub_industry_gics': 'Software', 'sector_id': 1, 'sector_gics': 'Information Technology'},
        {'id': 2, 'sub_industry_gics': 'Hardware', 'sector_id': 1, 'sector_gics': 'Information Technology'}
    ]
    
    with patch('backend.etl.transform.models.industry.subindustry_model.SubIndustry', spec=True) as mock_subindustry:
        mock_subindustry.side_effect = lambda **kwargs: SubIndustry(**kwargs)
        
        sector_avg = SectorFinancialAverage.from_sector("Information Technology", mock_cursor)
        
        assert sector_avg.sector_name == "Information Technology"
        assert len(sector_avg.sub_industries) == 2
        mock_cursor.execute.assert_called_once()

def test_get_sector_averages(mock_cursor):
    """Test getting sector averages for a metric."""
    mock_cursor.fetchall.return_value = [
        {'quarter': datetime(2023, 3, 31), 'avg_value': 1000000000},
        {'quarter': datetime(2022, 12, 31), 'avg_value': 950000000}
    ]
    
    result = SectorFinancialAverage.get_sector_averages("Information Technology", "revenue", mock_cursor)
    
    assert len(result) == 2
    assert result[str(datetime(2023, 3, 31))] == 1000000000
    assert result[str(datetime(2022, 12, 31))] == 950000000
    mock_cursor.execute.assert_called_once()

def test_get_sub_industries_in_sector(mock_cursor):
    """Test getting sub-industries in a sector."""
    mock_cursor.fetchall.return_value = [
        {'sub_industry_gics': 'Software'},
        {'sub_industry_gics': 'Hardware'}
    ]
    
    result = SectorFinancialAverage.get_sub_industries_in_sector("Information Technology", mock_cursor)
    
    assert len(result) == 2
    assert "Software" in result
    assert "Hardware" in result
    mock_cursor.execute.assert_called_once()

def test_calculate_sector_average_quarterly_financials(mock_cursor, sample_sub_industries):
    """Test calculating sector average quarterly financials."""
    # Mock get_sector_averages
    with patch.object(SectorFinancialAverage, 'get_sector_averages') as mock_get_averages:
        mock_get_averages.side_effect = [
            {str(datetime(2023, 3, 31)): 1000000000, str(datetime(2022, 12, 31)): 950000000},  # revenue
            {str(datetime(2023, 3, 31)): 200000000, str(datetime(2022, 12, 31)): 190000000}    # net_income
        ]
        
        sector_avg = SectorFinancialAverage("Information Technology", sample_sub_industries)
        result = sector_avg.calculate_sector_average_quarterly_financials(mock_cursor)
        
        assert result['sector'] == "Information Technology"
        assert result['total_revenue'] == 1000000000
        assert result['total_net_income'] == 200000000
        assert result['sub_industry_count'] == 2

def test_calculate_quarter_end_sector_average_pe_ratio(mock_cursor, sample_sub_industries):
    """Test calculating sector average PE ratio."""
    # Mock get_sub_industries_in_sector
    with patch.object(SectorFinancialAverage, 'get_sub_industries_in_sector') as mock_get_industries:
        mock_get_industries.return_value = ["Software", "Hardware"]
        
        # Mock get_companies_in_sub_industry
        with patch('backend.etl.transform.models.company.company_info_model.CompanyInfo.get_companies_in_sub_industry') as mock_get_companies:
            mock_get_companies.return_value = [
                {'id': 1, 'name': 'Company A', 'ticker': 'AAA'},
                {'id': 2, 'name': 'Company B', 'ticker': 'BBB'}
            ]
            
            # Mock calculate_average_pe
            with patch('backend.etl.transform.models.company.company_price_earnings_model.PriceEarningsRatio.calculate_average_pe') as mock_calc_pe:
                mock_calc_pe.side_effect = [20.0, 30.0, 25.0, 35.0]
                
                sector_avg = SectorFinancialAverage("Information Technology", sample_sub_industries)
                result = sector_avg.calculate_quarter_end_sector_average_pe_ratio(mock_cursor)
                
                assert result['avg_pe'] == 27.5
                assert result['median_pe'] == 27.5
                assert result['min_pe'] == 20.0
                assert result['max_pe'] == 35.0

def test_get_formatted_quarterly_averages(mock_cursor, sample_financial_data, sample_pe_data):
    """Test getting formatted quarterly averages."""
    # Setup mocks
    mock_cursor.fetchall.side_effect = [sample_financial_data, sample_pe_data]
    
    result = SectorFinancialAverage.get_formatted_quarterly_averages("Information Technology", mock_cursor)
    
    assert len(result) == 2
    assert result[0].quarter == "2023-Q1"
    assert result[0].revenue == 1000000000
    assert result[0].net_income == 200000000
    assert result[0].earnings_per_share == 2.5
    assert result[0].profit_margin == 20.0
    assert result[0].price_earnings_ratio == 25.5
    
    assert mock_cursor.execute.call_count == 2

def test_calculate_sector_average_quarterly_financials_with_history(mock_cursor, sample_sub_industries):
    """Test calculating sector average quarterly financials with history."""
    # Mock calculate_sector_average_quarterly_financials
    with patch.object(SectorFinancialAverage, 'calculate_sector_average_quarterly_financials') as mock_calc:
        mock_calc.return_value = {
            'sector': 'Information Technology',
            'total_revenue': 1000000000,
            'total_net_income': 200000000,
            'total_market_cap': 0,
            'sub_industry_count': 2
        }
        
        # Mock get_formatted_quarterly_averages
        with patch.object(SectorFinancialAverage, 'get_formatted_quarterly_averages') as mock_format:
            q_avg1 = SectorQuarterlyAverage(
                quarter="2023-Q1",
                revenue=1000000000,
                net_income=200000000,
                earnings_per_share=2.5,
                profit_margin=20.0,
                price_earnings_ratio=25.5
            )
            q_avg2 = SectorQuarterlyAverage(
                quarter="2022-Q4", 
                revenue=950000000,
                net_income=190000000,
                earnings_per_share=2.4,
                profit_margin=19.5,
                price_earnings_ratio=24.0
            )
            mock_format.return_value = [q_avg1, q_avg2]
            
            sector_avg = SectorFinancialAverage("Information Technology", sample_sub_industries)
            result = sector_avg.calculate_sector_average_quarterly_financials_with_history(mock_cursor)
            
            assert result['sector'] == "Information Technology"
            assert result['total_revenue'] == 1000000000
            assert 'quarterly_history' in result
            assert result['quarterly_history']['quarters'] == ["2023-Q1", "2022-Q4"]
            assert result['quarterly_history']['revenues'] == [1000000000, 950000000]
            assert result['quarterly_history']['net_incomes'] == [200000000, 190000000]
            assert result['quarterly_history']['eps_values'] == [2.5, 2.4]
            assert result['quarterly_history']['profit_margins'] == [20.0, 19.5]
            assert result['quarterly_history']['pe_ratios'] == [25.5, 24.0]

def test_get_sector_averages_no_data(mock_cursor):
    """Test getting sector averages when no data exists."""
    mock_cursor.fetchall.return_value = []
    result = SectorQuarterlyAverageFinancials.get_sector_averages("NonExistentSector", "revenue", mock_cursor)
    assert result == {}

def test_calculate_quarter_end_sector_average_pe_ratio_no_companies(mock_cursor):
    """Test PE ratio calculation when no companies exist."""
    with patch.object(SectorQuarterlyAverageFinancials, 'get_sub_industries_in_sector') as mock_get_industries:
        mock_get_industries.return_value = []
        result = SectorQuarterlyAverageFinancials.calculate_quarter_end_sector_average_pe_ratio(
            "Information Technology", mock_cursor)
        assert result == {}

def test_to_dict_with_missing_data(mock_cursor):
    """Test to_dict method with missing optional data."""
    sector_avg = SectorQuarterlyAverageFinancials(
        quarter="2023-Q1",
        sector_name="Information Technology",
        quarterly_avg_revenue=1000000000,
        quarterly_avg_net_income=200000000,
        quarterly_avg_earnings_per_share=2.5,
        quarterly_avg_profit_margin=None,
        quarterly_avg_price_earnings_ratio=None
    )
    
    result = sector_avg.to_dict()
    assert result['sector'] == "Information Technology"
    assert result['quarterly_avg_profit_margin'] is None
    assert result['quarterly_avg_price_earnings_ratio'] is None

def test_calculate_sector_average_quarterly_financials():
    # Test implementation
    pass
