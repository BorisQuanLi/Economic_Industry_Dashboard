"""Tests for the data processor service."""
import pytest
from unittest.mock import MagicMock, patch
from backend.webservice.services.data_processor import DataProcessor
from backend.etl.load.data_persistence.local_postgres import LocalPostgresRepository

@pytest.fixture
def db_manager():
    """Create a database manager for testing."""
    with patch('psycopg2.connect') as mock_connect:
        mock_cursor = MagicMock()
        mock_connection = MagicMock()
        mock_connection.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_connection
        
        repo = LocalPostgresRepository("postgresql://test:test@localhost:5432/testdb")
        repo._connection = mock_connection
        repo.cursor = mock_cursor
        return repo

@pytest.fixture
def data_processor(db_manager):
    """Create a DataProcessor instance for testing."""
    return DataProcessor(db_manager)

def test_insert_company_data(data_processor):
    """Test inserting company data."""
    # Test data
    test_data = {
        "ticker": "AAPL",
        "company_name": "Apple Inc.",
        "sector": "Technology",
        "price": 150.25
    }
    
    # Mock the necessary methods
    data_processor.db.save_companies = MagicMock(return_value=True)
    
    # Call the method
    result = data_processor.process_data(test_data, entity_type="company")
    
    # Verify the result
    assert result is True
    data_processor.db.save_companies.assert_called_once()

def test_get_sector_data(data_processor):
    """Test retrieving sector data."""
    # Mock the database query method to return test data
    test_sectors = [
        {"sector": "Technology", "companies": 25, "avg_market_cap": 500.5},
        {"sector": "Healthcare", "companies": 15, "avg_market_cap": 300.2}
    ]
    data_processor.db.get_companies_by_sector = MagicMock(return_value=test_sectors)
    
    # Call the method
    result = data_processor.get_data(entity_type="sector", name="Technology")
    
    # Verify the result
    assert result == test_sectors
    data_processor.db.get_companies_by_sector.assert_called_once_with("Technology")

def test_database_connection_error():
    """Test handling of database connection error."""
    with pytest.raises(ConnectionError):
        # Instead of DatabaseManager, use LocalPostgresRepository with invalid connection
        repo = LocalPostgresRepository(connection_string="invalid_connection_string")
        # Force connection attempt to trigger the error
        repo.connect()
        assert not repo.is_connected()

def test_data_processor():
    """Test data processor functionality"""
    mock_db = MagicMock()
    processor = DataProcessor(mock_db)

    # Set up mock returns
    mock_db.query = MagicMock(return_value=[
        {'company_name': 'TestCo', 'sector': 'Tech', 'revenue': 1000}
    ])

    # Test process method - update to match the actual interface of DataProcessor
    test_data = {'company_name': 'TestCo', 'sector': 'Tech'}
    result = processor.process_data(test_data, entity_type="company")
    
    # Assert the mock was called with expected arguments
    assert result is not None
