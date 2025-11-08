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
        mock_cursor.fetchall.return_value = [
            ('Information Technology', 2020, 4, 1000, 500, 2.5, 0.15),
            ('Health Care', 2020, 4, 2000, 800, 3.2, 0.18)
        ]
        
        flask_app = create_app(db_name='investment_analysis_test', db_user='postgres', db_password='postgres', testing=True)
        yield flask_app

@pytest.fixture
def client(app):
    return app.test_client()
