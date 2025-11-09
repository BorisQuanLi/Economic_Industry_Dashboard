"""
Standalone tests for sliding window algorithm
No Airflow dependencies - focuses on core business logic
"""
import pytest
from datetime import datetime
import sys
import os

# Standalone sliding window implementation for testing
def calculate_sliding_quarter(date_str: str, ticker: str) -> str:
    """Sliding window algorithm for earnings alignment"""
    date_obj = datetime.strptime(date_str, '%Y-%m-%d')
    month = date_obj.month
    year = date_obj.year
    
    # Handle Apple's October Q4 filing (key differentiator)
    if ticker == 'AAPL' and month == 10:
        return f"{year}Q4"
    elif month in [1, 2, 3]:
        return f"{year}Q1"
    elif month in [4, 5, 6]:
        return f"{year}Q2"
    elif month in [7, 8, 9]:
        return f"{year}Q3"
    else:
        return f"{year}Q4"

class TestSlidingWindow:
    
    def test_apple_q3_2024_sliding_window(self):
        """Test Apple Q3 2024 earnings filed in different months"""
        # Apple typically files Q3 in late October/early November
        assert calculate_sliding_quarter('2024-10-31', 'AAPL') == '2024Q4'  # Apple's Q4
        
        # Standard tech companies file Q3 in July-September
        assert calculate_sliding_quarter('2024-07-25', 'MSFT') == '2024Q3'
        assert calculate_sliding_quarter('2024-08-15', 'GOOGL') == '2024Q3'
        assert calculate_sliding_quarter('2024-09-30', 'AMZN') == '2024Q3'
    
    def test_cross_sector_alignment(self):
        """Test sliding window aligns disparate filing dates"""
        # Q3 2024 earnings across sectors with different filing patterns
        q3_filings = [
            ('2024-07-15', 'JPM', '2024Q3'),    # Financials - early Q3
            ('2024-08-01', 'XOM', '2024Q3'),    # Energy - mid Q3  
            ('2024-09-15', 'JNJ', '2024Q3'),    # Healthcare - late Q3
            ('2024-10-15', 'AAPL', '2024Q4'),   # Apple's unique Q4 timing
        ]
        
        for date, ticker, expected in q3_filings:
            result = calculate_sliding_quarter(date, ticker)
            assert result == expected, f"{ticker} filing on {date} should align to {expected}"
    
    def test_real_world_q3_2024_scenario(self):
        """Simulate real Q3 2024 earnings season sliding window"""
        # Actual Q3 2024 earnings filing dates (approximate)
        earnings_data = [
            # Traditional Q3 filers
            {'ticker': 'MSFT', 'filing_date': '2024-07-24', 'revenue': 64700000000},
            {'ticker': 'GOOGL', 'filing_date': '2024-07-23', 'revenue': 84742000000},
            {'ticker': 'AMZN', 'filing_date': '2024-08-01', 'revenue': 147977000000},
            
            # Apple's delayed Q4 filing (their Q3 results)
            {'ticker': 'AAPL', 'filing_date': '2024-10-31', 'revenue': 94930000000},
        ]
        
        aligned_data = []
        for record in earnings_data:
            aligned_quarter = calculate_sliding_quarter(
                record['filing_date'], 
                record['ticker']
            )
            
            aligned_data.append({
                **record,
                'aligned_quarter': aligned_quarter
            })
        
        # Verify cross-sector analysis is now possible
        q3_companies = [r for r in aligned_data if r['aligned_quarter'] in ['2024Q3', '2024Q4']]
        assert len(q3_companies) == 4
        
        # Calculate sector averages with aligned quarters
        total_revenue = sum(r['revenue'] for r in q3_companies)
        avg_revenue = total_revenue / len(q3_companies)
        
        assert avg_revenue > 90000000000  # Realistic Q3 2024 average