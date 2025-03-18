"""Repository interfaces for data access across ETL pipeline."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

class DataRepository(ABC):
    """Base repository interface for data access operations."""
    
    @abstractmethod
    def connect(self) -> bool:
        """Establish connection to data source."""
        pass
    
    @abstractmethod
    def close(self) -> None:
        """Close connection to data source."""
        pass

class ExtractRepository(DataRepository):
    """Repository interface for extract phase operations."""
    
    @abstractmethod
    def extract_companies(self) -> List[Dict[str, Any]]:
        """Extract raw company data."""
        pass
    
    @abstractmethod
    def extract_sectors(self) -> List[Dict[str, Any]]:
        """Extract raw sector data."""
        pass
    
    @abstractmethod
    def extract_sub_sectors(self) -> List[Dict[str, Any]]:
        """Extract raw sub-sector data."""
        pass

class TransformRepository(DataRepository):
    """Repository interface for transform phase operations."""
    
    @abstractmethod
    def get_companies_by_sector(self, sector: str) -> List[Dict[str, Any]]:
        """Get transformed company data by sector."""
        pass
    
    @abstractmethod
    def get_sector_metrics(self, sector: str) -> Dict[str, Any]:
        """Get transformed metrics for a sector."""
        pass
    
    @abstractmethod
    def get_sub_sector_metrics(self, sub_sector: str) -> Dict[str, Any]:
        """Get transformed metrics for a sub-sector."""
        pass

class LoadRepository(DataRepository):
    """Repository interface for load phase operations."""
    
    @abstractmethod
    def save_companies(self, companies: List[Dict[str, Any]]) -> None:
        """Save company data to destination."""
        pass
    
    @abstractmethod
    def save_sectors(self, sectors: List[Dict[str, Any]]) -> None:
        """Save sector data to destination."""
        pass
    
    @abstractmethod
    def save_sub_sectors(self, sub_sectors: List[Dict[str, Any]]) -> None:
        """Save sub-sector data to destination."""
        pass
    
    @abstractmethod
    def save_metrics(self, entity_type: str, entity_id: str, metrics: Dict[str, Any]) -> None:
        """Save metrics for a specific entity."""
        pass

__all__ = ['DataRepository', 'ExtractRepository', 'TransformRepository', 'LoadRepository']
