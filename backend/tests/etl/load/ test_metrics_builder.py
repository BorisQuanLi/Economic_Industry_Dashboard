import pytest
from etl.load.builders.metrics import MetricsBuilder

def test_metrics_builder_validation():
    builder = MetricsBuilder()
    
    with pytest.raises(ValueError):
        builder.build({})  # Empty dict should fail
        
    with pytest.raises(ValueError):
        builder.build({'company_id': 1})  # Missing required fields
        
def test_metrics_builder_ratios():
    builder = MetricsBuilder()
    test_data = {
        'company_id': 1,
        'period': '2023-Q1',
        'values': {
            'revenue': 1000,
            'net_income': 100
        }
    }
    
    result = builder.build(test_data)
    assert result['metrics']['profit_margin'] == 0.1
    
def test_metrics_builder_structure():
    builder = MetricsBuilder()
    test_data = {
        'company_id': 1,
        'period': '2023-Q1',
        'values': {
            'revenue': 1000
        }
    }
    
    result = builder.build(test_data)
    assert 'company_id' in result
    assert 'period' in result
    assert 'metrics' in result
    assert result['metrics']['revenue'] == 1000
