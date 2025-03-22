import pytest
from unittest.mock import MagicMock, patch
from backend.webservice.services.db_operations import DBOperations

@pytest.fixture
def db_manager():
    """Create a database repository for testing."""
    with patch('psycopg2.connect', autospec=True) as mock_connect:
        with patch('backend.etl.load.data_persistence.local_postgres.LocalPostgresRepository.connect') as mock_repo_connect:
            mock_cursor = MagicMock()
            mock_connection = MagicMock()
            mock_connection.closed = 0
            mock_connection.cursor.return_value = mock_cursor
            mock_connect.return_value = mock_connection
            mock_repo_connect.return_value = True
            
            from backend.etl.load.data_persistence.local_postgres import LocalPostgresRepository
            repo = LocalPostgresRepository("mock://connection")
            repo._connection = mock_connection
            repo.cursor = mock_cursor
            yield repo

def test_insert_company_data(db_manager):
    """Test inserting company data"""
    test_data = {"symbol": "AAPL", "name": "Apple Inc", "sector": "Technology"}
    result = db_manager.save(test_data)
    assert result is True
    db_manager.cursor.execute.assert_called_once()

def test_failed_insert_company_data(db_manager):
    """Test failed company data insertion"""
    db_manager.cursor.execute.side_effect = Exception("Database error")
    result = db_manager.save_dataframe({}, "companies")
    assert result is False
    db_manager._connection.rollback.assert_called_once()

def test_get_sector_data(db_manager):
    """Test retrieving sector data"""
    expected_data = [("Technology", 5)]
    db_manager.cursor.fetchall.return_value = expected_data
    db_manager.cursor.description = [("sector",), ("count",)]
    
    result = db_manager.read_data("SELECT sector, COUNT(*) FROM companies GROUP BY sector")
    assert len(result) == 1
    assert result[0]["sector"] == "Technology"
    assert result[0]["count"] == 5
