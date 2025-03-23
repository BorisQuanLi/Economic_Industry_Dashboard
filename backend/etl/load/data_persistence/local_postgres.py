import logging
import pandas as pd
from io import StringIO
from typing import Dict, List, Any, Optional, Type, TypeVar, Union
import psycopg2
from psycopg2.extras import RealDictCursor
from flask import g, current_app
from .base_database_repository import DatabaseRepository
from ....etl.config import get_config, DatabaseConfig  # Fix import path

logger = logging.getLogger(__name__)

T = TypeVar('T')

class LocalPostgresRepository(DatabaseRepository):
    """
    Repository for storing and retrieving data from a PostgreSQL database.
    
    This class provides both direct database access methods and Flask-specific
    context management to ensure proper connection handling in web applications.
    """

    def __init__(self, connection_string: Optional[str] = None, db_config: Optional[DatabaseConfig] = None):
        """Initialize the repository with connection details.
        
        Args:
            connection_string (str, optional): Database connection string
            db_config (DatabaseConfig, optional): Database configuration
        """
        if connection_string:
            self._connection_string = connection_string
        elif db_config:
            self._connection_string = db_config.uri
        else:
            self._connection_string = get_config().db.uri
            
        self._connection = None
        self.cursor = None
        self.connect()

    def connect(self):
        """Connect to database."""
        try:
            if isinstance(self._connection_string, dict):
                # Convert dict to connection string
                conn_params = {
                    'host': self._connection_string.get('host', 'localhost'),
                    'port': self._connection_string.get('port', 5432),
                    'database': self._connection_string.get('database', 'postgres'),
                    'user': self._connection_string.get('user', 'postgres'),
                    'password': self._connection_string.get('password', '')
                }
                self._connection = psycopg2.connect(**conn_params)
            else:
                self._connection = psycopg2.connect(self._connection_string)
            
            # Set cursorclass
            self._connection.cursor_factory = RealDictCursor
            self.cursor = self._connection.cursor()
            return self._connection
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            raise

    def save_dataframe(self, data: pd.DataFrame, table_name: str, if_exists="replace") -> bool:
        """Save a pandas DataFrame to the database."""
        try:
            # Insert data logic here
            # For example:
            columns = ', '.join(data.keys())
            values = ', '.join([f"'{v}'" for v in data.values()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values})"
            self.cursor.execute(query)
            self._connection.commit()
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            self._connection.rollback()
            return False

    def read_data(self, query: str) -> List[Dict[str, Any]]:
        """Read data from the database using a SQL query."""
        try:
            if self._connection is None:
                self.connect()
            
            self.cursor.execute(query)
            columns = [desc[0] for desc in self.cursor.description]
            result = []
            
            for row in self.cursor.fetchall():
                result.append(dict(zip(columns, row)))
            
            return result
        except Exception as e:
            logger.error(f"Error reading data: {e}")
            return []

    def close(self) -> None:
        """Close the database connection."""
        if self._connection is not None:
            if self.cursor is not None:
                self.cursor.close()
                self.cursor = None
            self._connection.close()
            self._connection = None
            
    def is_connected(self) -> bool:
        """Check if database is connected."""
        return self._connection is not None and self._connection.closed == 0

    def save(self, data):
        """Implement abstract save method."""
        try:
            if isinstance(data, dict):
                df = pd.DataFrame([data])
            elif isinstance(data, pd.DataFrame):
                df = data
            else:
                return False
            
            if len(df) == 0:
                return False
                
            # Convert values to strings and escape quotes
            values = [str(v).replace("'", "''") for v in df.iloc[0]]
            columns = df.columns.tolist()
            columns_str = ', '.join(columns)
            values_str = ', '.join([f"'{v}'" for v in values])
            
            query = f"INSERT INTO default_table ({columns_str}) VALUES ({values_str})"
            self.cursor.execute(query)
            self._connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error in save: {e}")
            if self._connection:
                self._connection.rollback()
            return False

    def get(self, query):
        """Implement abstract get method."""
        try:
            return self.read_data(query)
        except Exception as e:
            logger.error(f"Error in get: {e}")
            return []

    def delete(self, query):
        """Implement abstract delete method."""
        try:
            if self._connection is None:
                self.connect()
            self.cursor.execute(query)
            self._connection.commit()
            return True
        except Exception as e:
            logger.error(f"Error in delete: {e}")
            self._connection.rollback()
            return False

    # Domain object construction utilities (from connection.py)
    def build_from_record(self, Class: Type[T], record) -> Optional[T]:
        """Build a domain object from a database record."""
        if not record:
            return None
        attr = dict(zip(Class.columns, record))
        obj = Class()
        obj.__dict__ = attr
        return obj

    def build_from_records(self, Class: Type[T], records) -> List[T]:
        """Build multiple domain objects from database records."""
        return [self.build_from_record(Class, record) for record in records]

    # Common query operations (from connection.py)
    def find_all(self, Class: Type[T]) -> List[T]:
        """Find all records for a domain class."""
        sql_str = f"SELECT * FROM {Class.__table__}"
        self.cursor.execute(sql_str)
        records = self.cursor.fetchall()
        return self.build_from_records(Class, records)

    def find(self, Class: Type[T], id: int) -> Optional[T]:
        """Find a record by ID."""
        sql_str = f"SELECT * FROM {Class.__table__} WHERE id = %s"
        self.cursor.execute(sql_str, (id,))
        record = self.cursor.fetchone()
        return self.build_from_record(Class, record)

    def find_by_field(self, Class: Type[T], field: str, value: Any) -> Optional[T]:
        """Find a record by a specific field value."""
        sql_str = f"SELECT * FROM {Class.__table__} WHERE {field} = %s"
        self.cursor.execute(sql_str, (value,))
        record = self.cursor.fetchone()
        return self.build_from_record(Class, record)

    def execute_query(self, query: str, params: tuple = None) -> None:
        """Execute a database query."""
        self.cursor.execute(query, params or ())
        self._connection.commit()

    # Flask-specific context management methods
    @staticmethod
    def get_db_in_context():
        """
        Get or create database connection in Flask application context.
        
        Returns:
            psycopg2.connection: Database connection
        """
        if "db" not in g:
            config = get_config()
            # Create repository
            repo = LocalPostgresRepository(db_config=config.db)
            # Store both the repository and its connection
            g.db_repo = repo
            g.db = repo._connection
            g.db_cursor = repo.cursor
        return g.db

    @staticmethod
    def get_repo_in_context():
        """
        Get or create LocalPostgresRepository in Flask application context.
        
        Returns:
            LocalPostgresRepository: Repository for database operations
        """
        if "db_repo" not in g:
            LocalPostgresRepository.get_db_in_context()  # This will create both db and db_repo
        return g.db_repo

    @staticmethod
    def close_db_in_context(e=None):
        """Close database connection when Flask application context ends."""
        db_repo = g.pop("db_repo", None)
        if db_repo is not None:
            db_repo.close()
        # These will be closed by the repository, but we'll also remove them from g
        g.pop("db", None)
        g.pop("db_cursor", None)

    # Standalone connection getter (non-Flask context)
    @staticmethod
    def get_standalone_connection():
        """Get standalone database connection (non-Flask context)."""
        config = get_config()
        repo = LocalPostgresRepository(db_config=config.db)
        return repo._connection
