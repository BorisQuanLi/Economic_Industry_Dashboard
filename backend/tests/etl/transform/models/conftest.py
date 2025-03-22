"""Shared test fixtures for model tests."""
import pytest
from unittest.mock import Mock
from datetime import datetime

@pytest.fixture
def mock_cursor():
    cursor = Mock()
    cursor.fetchone.return_value = None
    cursor.fetchall.return_value = []
    return cursor

@pytest.fixture
def sample_quarterly_data():
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

@pytest.fixture
def sample_sector_financial_data():
    """Sample financial data for sector testing."""
    return {
        'sector_name': 'Information Technology',
        'quarterly_avg_revenue': 5000000000,
        'quarterly_avg_net_income': 1000000000,
        'quarterly_avg_earnings_per_share': 2.5,
        'quarterly_avg_profit_margin': 20.0,
        'quarterly_avg_price_earnings_ratio': 25.0
    }

@pytest.fixture
def sample_subindustry_financial_data():
    """Sample financial data for sub-industry testing."""
    return {
        'sub_industry_name': 'Software',
        'quarterly_avg_revenue': 1000000000,
        'quarterly_avg_net_income': 200000000,
        'quarterly_avg_earnings_per_share': 2.5,
        'quarterly_avg_profit_margin': 20.0,
        'quarterly_avg_price_earnings_ratio': 25.0
    }
