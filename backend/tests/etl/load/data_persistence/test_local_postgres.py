import pytest
from unittest.mock import MagicMock, patch
from backend.etl.load.data_persistence.local_postgres import LocalPostgresRepository

@pytest.fixture
def postgres_repo():
    """Create a mocked repository instance for unit testing."""
    mock_cursor = MagicMock()
    mock_connection = MagicMock()
    mock_connection.closed = 0
    mock_connection.cursor.return_value = mock_cursor
    mock_connection.close = MagicMock()  # Explicitly add close method
    
    with patch('psycopg2.connect', autospec=True) as mock_connect:
        mock_connect.return_value = mock_connection
        repo = LocalPostgresRepository("mock://connection")
        repo._connection = mock_connection  # Ensure connection is set
        repo.cursor = mock_cursor
        yield repo

@pytest.mark.unit
def test_connect(postgres_repo):
    """Test successful database connection."""
    assert postgres_repo.is_connected() is True

@pytest.mark.unit
def test_close_connection(postgres_repo):
    """Test closing the database connection."""
    mock_connection = postgres_repo._connection
    mock_cursor = postgres_repo.cursor
    
    postgres_repo.close()
    
    mock_cursor.close.assert_called_once()
    mock_connection.close.assert_called_once()
    assert postgres_repo._connection is None
    assert postgres_repo.cursor is None

@pytest.mark.unit
def test_is_connected(postgres_repo):
    """Test connection status check."""
    assert postgres_repo.is_connected() is True
    postgres_repo._connection.closed = 1
    assert postgres_repo.is_connected() is False

# Integration tests that require a real database
@pytest.mark.integration
@pytest.mark.skipif(
    "os.environ.get('INTEGRATION_TESTS') != 'true'",
    reason="Integration tests require database and INTEGRATION_TESTS=true"
)
def test_real_database_connection():
    """Test connecting to real database."""
    repo = LocalPostgresRepository(
        "postgresql://postgres:postgres@localhost:5432/testdb"
    )
    assert repo.is_connected()
    repo.close()
