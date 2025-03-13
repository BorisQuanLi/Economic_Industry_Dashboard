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
