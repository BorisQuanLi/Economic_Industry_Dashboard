"""Base repository implementations."""
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Generator
from sqlalchemy.orm import Session

class DataRepository(ABC):
    @abstractmethod
    def get_sectors(self) -> List[str]:
        pass
        
    @abstractmethod
    def get_sector_metrics(self, sector: str) -> Dict[str, Any]:
        pass
        
    @abstractmethod
    def store_raw_data(self, data: Dict[str, Any], dataset_name: str) -> bool:
        pass

class DatabaseRepository(ABC):
    """Abstract base class for database operations."""
    
    @abstractmethod
    def _create_engine(self):
        pass
    
    @abstractmethod
    def get_session(self) -> Generator[Session, None, None]:
        pass
    
    @abstractmethod
    def store_raw_data(self, data: Dict[str, Any], dataset_name: str) -> bool:
        pass
    
    @abstractmethod
    def connect(self):
        """Establish connection to the database"""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close the database connection"""
        pass
    
    @abstractmethod
    def execute_query(self, query, params=None):
        """Execute a database query"""
        pass
    
    @abstractmethod
    def fetch_data(self, query, params=None):
        """Fetch data from the database"""
        pass
    
    @abstractmethod
    def insert_data(self, table, data):
        """Insert data into a database table"""
        pass
    
    @abstractmethod
    def update_data(self, table, data, condition):
        """Update data in a database table"""
        pass
    
    @abstractmethod
    def delete_data(self, table, condition):
        """Delete data from a database table"""
        pass

import pandas as pd

class BaseRepository(ABC):
    """Base abstract class for all data repositories"""
    
    @abstractmethod
    def connect(self):
        """Connect to the data source"""
        pass
    
    @abstractmethod
    def is_connected(self):
        """Check if connected to data source"""
        pass
    
    @abstractmethod
    def close(self):
        """Close connection to data source"""
        pass
    
    @abstractmethod
    def save_dataframe(self, df, table_name, **kwargs):
        """Save a pandas DataFrame to the data source"""
        pass
    
    @abstractmethod
    def query(self, query_string, **kwargs):
        """Execute a query against the data source and return results"""
        pass

class DataPersistenceBase(ABC):
    """Base class for data persistence implementations."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Connect to the data store."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close the connection to the data store."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to the data store."""
        pass
    
    @abstractmethod
    def save_dataframe(self, data: Any, location: str) -> bool:
        """Save data to the specified location."""
        pass
    
    @abstractmethod
    def read_data(self, query: str) -> List[Dict[str, Any]]:
        """Read data using the specified query."""
        pass
