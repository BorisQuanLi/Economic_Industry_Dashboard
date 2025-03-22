"""Tests for ETL load functionality."""
import pytest
from backend.etl.load.financial_data import FinancialDataBuilder  # Updated import
from backend.etl.load.builders.financial_metrics import FinancialMetrics
from backend.etl.load.data_persistence.base_database_repository import DatabaseRepository

def test_financial_data_loading():
    """Test financial data loading process"""
    # Create test instance
    builder = FinancialDataBuilder()
    
    # Test with sample data
    sample_data = {"ticker": "AAPL", "price": 150.75}
    result = builder.build_financial_data(sample_data)
    
    # Verify result
    assert result is not None
    assert result == sample_data
    assert "ticker" in result
    assert result["ticker"] == "AAPL"
    assert "price" in result
    assert result["price"] == 150.75

def test_metrics_calculation():
    """Test financial metrics calculation"""
    # Create test instance
    metrics = FinancialMetrics()
    
    # Test growth rate calculation
    initial_value = 100
    final_value = 121
    periods = 2
    growth_rate = metrics.calculate_growth_rate(initial_value, final_value, periods)
    assert round(growth_rate, 4) == 0.1000  # 10% growth rate
    
    # Test margin calculation
    revenue = 1000
    profit = 200
    margin = metrics.calculate_margin(revenue, profit)
    assert margin == 0.2  # 20% margin
