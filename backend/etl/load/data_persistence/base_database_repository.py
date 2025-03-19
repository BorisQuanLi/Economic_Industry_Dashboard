"""Base database repository implementation providing core database functionality."""

from abc import ABC, abstractmethod
from backend.common.repositories import DataRepository

class DatabaseRepository(ABC):
    """Abstract base class for database repositories"""
    
    @abstractmethod
    def save(self, data):
        """Save data to the repository"""
        pass

    @abstractmethod
    def get(self, query):
        """Retrieve data from the repository"""
        pass

    @abstractmethod
    def delete(self, query):
        """Delete data from the repository"""
        pass
