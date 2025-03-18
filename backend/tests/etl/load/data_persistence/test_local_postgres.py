import pytest
import pandas as pd
from unittest.mock import patch, MagicMock
from backend.etl.load.data_persistence.local_postgres import LocalPostgresRepository

@pytest.fixture
def mock_connection():
    """Create a mock database connection"""
    with patch('backend.etl.load.data_persistence.local_postgres.psycopg2') as mock_psycopg2:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_conn.cursor.return_value = mock_cursor
        mock_psycopg2.connect.return_value = mock_conn
        yield mock_conn

@pytest.fixture
def sample_data():
    """Generate sample dataframe for testing"""
    return pd.DataFrame({
        'ticker': ['AAPL', 'MSFT', 'GOOG'],
        'company_name': ['Apple Inc', 'Microsoft Corp', 'Alphabet Inc'],
        'sector': ['Technology', 'Technology', 'Technology'],
        'price': [150.75, 290.50, 2950.25]
    })

@pytest.fixture
def postgres_repo(mock_connection):
    """Create a LocalPostgresRepository instance with mocked connection"""
    # The error suggests LocalPostgresRepository doesn't accept 'host' parameter
    # Let's change to use connection_string instead, which is likely what the class expects
    repo = LocalPostgresRepository(
        connection_string="postgresql://testuser:testpass@localhost:5432/testdb"
    )
    # Or alternatively, if the class accepts a different set of parameters:
    # repo = LocalPostgresRepository(
    #     db_name='testdb',
    #     username='testuser',
    #     password='testpass',
    #     port=5432
    # )
    return repo

def test_connect(postgres_repo, mock_connection):
    """Test connection to database"""
    postgres_repo.connect()
    mock_connection.cursor.assert_called_once()
    assert postgres_repo.is_connected() is True

def test_save_dataframe(postgres_repo, sample_data):
    """Test saving a dataframe to database"""
    table_name = "companies"
    
    # Test saving data
    result = postgres_repo.save_dataframe(sample_data, table_name)
    
    # Verify the SQL execution was called
    cursor = postgres_repo.connection.cursor()
    assert cursor.execute.called
    
    # Verify commit was called
    postgres_repo.connection.commit.assert_called_once()
    
    assert result is True

def test_read_data(postgres_repo):
    """Test reading data from database"""
    # Mock the cursor fetchall to return sample data
    cursor = postgres_repo.connection.cursor()
    cursor.fetchall.return_value = [
        ('AAPL', 'Apple Inc', 'Technology', 150.75),
        ('MSFT', 'Microsoft Corp', 'Technology', 290.50)
    ]
    cursor.description = [
        ('ticker', None, None, None, None, None, None),
        ('company_name', None, None, None, None, None, None),
        ('sector', None, None, None, None, None, None),
        ('price', None, None, None, None, None, None)
    ]
    
    # Test querying data
    query = "SELECT * FROM companies WHERE sector = 'Technology'"
    result = postgres_repo.query(query)
    
    # Assert the query was executed
    cursor.execute.assert_called_with(query)
    
    # Check that result is a dataframe with expected shape
    assert isinstance(result, pd.DataFrame)
    assert result.shape[0] == 2
    assert 'ticker' in result.columns

def test_close_connection(postgres_repo):
    """Test closing the database connection"""
    postgres_repo.close()
    postgres_repo.connection.close.assert_called_once()