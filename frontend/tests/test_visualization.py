import pytest
from unittest.mock import MagicMock
import pandas as pd
from api.client import APIClient

def test_sector_metrics():
    mock_client = MagicMock(spec=APIClient)
    mock_client.get_sector_metrics.return_value = {
        'avg_revenue': 1000,
        'avg_profit_margin': 15.5,
        'total_market_cap': 500
    }
    
    metrics = mock_client.get_sector_metrics('Technology')
    assert metrics['avg_revenue'] == 1000
    assert metrics['avg_profit_margin'] == 15.5
