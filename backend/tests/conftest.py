from datetime import date
import pytest
from unittest.mock import patch, MagicMock
from api.src import create_app

@pytest.fixture(scope = 'module')
def app():
    with patch('psycopg2.connect') as mock_connect, \
         patch('api.src.db.db.get_db') as mock_get_db:
        
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_get_db.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Mock data for different queries
        mock_cursor.fetchone.return_value = (1, 'Application Software', 'Information Technology')
        
        # Mock data for companies table (used by get_all_company_names_in_sub_sector)
        mock_companies_data = [
            (1, 'Apple Inc.', 'AAPL', 1, 1976, 164000, 'CA'),
            (2, 'Microsoft Corp.', 'MSFT', 1, 1975, 181000, 'WA')
        ]

        # Mock data for quarterly_reports table
        mock_quarterly_reports_data = [
            (1, date(2020, 10, 1), 1, 1000, 500, 2.5, 0.15),
            (2, date(2020, 7, 1), 1, 900, 450, 2.0, 0.10)
        ]

        # Mock data for prices_pe table
        mock_prices_pe_data = [
            (1, date(2020, 10, 1), 1, 150.0, 25.0),
            (2, date(2020, 7, 1), 1, 140.0, 23.0)
        ]

        def execute_side_effect(query, params=None):
            query_lower = query.lower()
            if "select companies.* from companies" in query_lower:
                mock_cursor.fetchall.return_value = mock_companies_data
            elif "select quarterly_reports.* from quarterly_reports" in query_lower:
                mock_cursor.fetchall.return_value = mock_quarterly_reports_data
            elif "select prices_pe.* from prices_pe" in query_lower:
                mock_cursor.fetchall.return_value = mock_prices_pe_data
            else:
                mock_cursor.fetchall.return_value = [] # Default to empty list for unmocked queries

        mock_cursor.execute.side_effect = execute_side_effect
        
        flask_app = create_app(db_name='investment_analysis_test', db_user='postgres', db_password='postgres', testing=True)
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()
