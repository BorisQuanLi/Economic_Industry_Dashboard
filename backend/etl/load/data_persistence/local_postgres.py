import logging
import pandas as pd
from io import StringIO
from typing import Dict, List, Any
import psycopg2
from psycopg2.extras import RealDictCursor  # Add this import
from .base_database_repository import DatabaseRepository

logger = logging.getLogger(__name__)

class LocalPostgresRepository(DatabaseRepository):
    """Repository for storing data in a local PostgreSQL database."""

    def __init__(self, connection_string: str):
        """Initialize the repository with connection details.
        
        Args:
            connection_string (str): Database connection string
        """
        self._connection_string = connection_string
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
