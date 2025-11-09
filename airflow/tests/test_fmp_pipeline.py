"""
Tests for FMP Rate-Limited Pipeline
Demonstrates enterprise testing practices for Airflow DAGs
"""
import pytest
from datetime import datetime
from unittest.mock import patch, MagicMock
import sys
import os

# Add DAGs directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'dags'))

from fmp_rate_limited_pipeline import (
    calculate_sliding_quarter,
    get_sector_tickers,
    extract_with_sliding_window
)

class TestFMPPipeline:
    
    def test_sliding_window_apple_october(self):
        """Test Apple Q4 October filing alignment"""
        result = calculate_sliding_quarter('2023-10-15', 'AAPL')
        assert result == '2023Q4'
    
    def test_sliding_window_standard_quarters(self):
        """Test standard quarterly alignment"""
        assert calculate_sliding_quarter('2023-03-15', 'MSFT') == '2023Q1'
        assert calculate_sliding_quarter('2023-06-15', 'GOOGL') == '2023Q2'
        assert calculate_sliding_quarter('2023-09-15', 'AMZN') == '2023Q3'
        assert calculate_sliding_quarter('2023-12-15', 'TSLA') == '2023Q4'
    
    def test_sector_tickers_coverage(self):
        """Test all 11 S&P sectors have ticker mappings"""
        sectors = [
            'Energy', 'Consumer Staples', 'Real Estate', 'Health Care',
            'Information Technology', 'Financials', 'Materials', 'Industrials',
            'Consumer Discretionary', 'Utilities', 'Communication Services'
        ]
        
        for sector in sectors:
            tickers = get_sector_tickers(sector)
            assert len(tickers) > 0, f"No tickers found for {sector}"
        
        assert 'AAPL' in get_sector_tickers('Information Technology')
    
    @patch('fmp_rate_limited_pipeline.requests.get')
    def test_rate_limiting_retry(self, mock_get):
        """Test rate limiting retry logic"""
        mock_response_429 = MagicMock()
        mock_response_429.status_code = 429
        
        mock_response_200 = MagicMock()
        mock_response_200.status_code = 200
        mock_response_200.json.return_value = [
            {
                'date': '2023-09-30',
                'revenue': 1000000,
                'netIncome': 200000,
                'eps': 2.5
            }
        ]
        
        mock_get.side_effect = [mock_response_429, mock_response_200]
        
        with patch('fmp_rate_limited_pipeline.time.sleep'):
            result = extract_with_sliding_window('AAPL', 'test_key')
            
        assert len(result) == 1
        assert result[0]['ticker'] == 'AAPL'
        assert result[0]['aligned_quarter'] == '2023Q3'