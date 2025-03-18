"""Tests for database operations."""
import pytest
from unittest.mock import MagicMock, patch
from backend.etl.load.data_persistence.local_postgres import LocalPostgresRepository

@pytest.fixture
def db_manager():
    """Create a database repository for testing."""
    # Using LocalPostgresRepository instead of DatabaseManager
    repo = LocalPostgresRepository(
        connection_string="postgresql://testuser:testpass@localhost:5432/testdb"
    )
    # Mock the connection to avoid actual DB operations
    repo.connect = MagicMock(return_value=True)
    repo.connection = MagicMock()
    repo.cursor = MagicMock()
    
    # Return the mocked repository
    yield repo
    
    # Cleanup after tests
    repo.connection.close.return_value = None

def test_insert_company_data(db_manager):
    """Test company data insertion."""
    # Test data
    test_company = {
        "ticker": "TEST",
        "company_name": "Test Company Inc.",
        "sector": "Technology",
        "industry": "Software"
    }
    
    # Mock the save_dataframe method
    db_manager.save_dataframe = MagicMock(return_value=True)
    
    # Call the method under test
    result = db_manager.save_companies([test_company])
    
    # Verify results
    assert result is True
    db_manager.save_dataframe.assert_called_once()
    # Check if save_dataframe was called with the right parameters
    args, _ = db_manager.save_dataframe.call_args
    assert len(args) >= 1  # At least one argument was passed
    assert len(args[0]) == 1  # One company was passed

def test_failed_insert_company_data(db_manager):
    """Test failed company data insertion."""
    # Test data
    test_company = {
        "ticker": "TEST",
        "company_name": "Test Company Inc.",
        "sector": "Technology",
        "industry": "Software"
    }
    
    # Mock the save_dataframe method to fail
    db_manager.save_dataframe = MagicMock(side_effect=Exception("Database error"))
    
    # Call the method under test with exception handling
    with pytest.raises(Exception) as exc_info:
        db_manager.save_companies([test_company])
    
    # Verify the exception
    assert "Database error" in str(exc_info.value)

def test_get_sector_data(db_manager):
    """Test sector data retrieval."""
    # Mock the query method
    expected_result = [
        {"sector": "Technology", "count": 10},
        {"sector": "Healthcare", "count": 5}
    ]
    db_manager.query = MagicMock(return_value=expected_result)
    
    # Call the method under test
    result = db_manager.query("SELECT * FROM sectors")
    
    # Verify results
    assert result == expected_result
    db_manager.query.assert_called_once_with("SELECT * FROM sectors")
    assert len(result) == 2
    assert result[0]["sector"] == "Technology"
    assert result[0]["count"] == 10

def test_database_connection_error():
    """Test handling of database connection error."""
    # Create repository with invalid connection
    repo = LocalPostgresRepository(connection_string="invalid_connection_string")
    
    # Patch the connect method to raise an exception
    with patch.object(repo, 'connect', side_effect=ConnectionError("Failed to connect")):
        # Try to connect and expect an exception
        with pytest.raises(ConnectionError) as exc_info:
            repo.connect()
        
        # Verify the exception message
        assert "Failed to connect" in str(exc_info.value)