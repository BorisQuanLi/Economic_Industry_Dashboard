import pytest
import pandas as pd
from backend.data_processor import DataProcessor

def test_calculate_sector_metrics():
    sample_data = pd.DataFrame({
        'company_name': ['A', 'B', 'C'],
        'sector': ['Tech', 'Tech', 'Tech'],
        'revenue': [100, 200, 300],
        'profit': [10, 20, 30],
        'market_cap': [1000, 2000, 3000]
    })
    
    processor = DataProcessor(sample_data)
    metrics = processor.calculate_sector_metrics('Tech')
    
    assert metrics['avg_revenue'] == 200
    assert metrics['total_market_cap'] == 6000
    assert 'profit_margin' in metrics

def test_filter_invalid_data():
    sample_data = pd.DataFrame({
        'company_name': ['A', 'B', 'C'],
        'sector': ['Tech', 'Tech', 'Tech'],
        'revenue': [100, -200, 300],  # Invalid negative revenue
        'profit': [10, 20, None],     # Missing profit
        'market_cap': [1000, 2000, 3000]
    })
    
    processor = DataProcessor(sample_data)
    clean_data = processor.clean_data()
    
    assert len(clean_data) == 1  # Only company A should remain
    assert clean_data.iloc[0]['company_name'] == 'A'

def test_time_series_aggregation():
    sample_ts_data = pd.DataFrame({
        'date': pd.date_range(start='2023-01-01', periods=4, freq='M'),
        'sector': ['Tech'] * 4,
        'revenue': [100, 110, 120, 130]
    })
    
    processor = DataProcessor(sample_ts_data)
    quarterly_data = processor.aggregate_by_quarter('Tech')
    
    assert len(quarterly_data) == 2  # Should aggregate into 2 quarters
    assert quarterly_data['revenue'].sum() == 460
