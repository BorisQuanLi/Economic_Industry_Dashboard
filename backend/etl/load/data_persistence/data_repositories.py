"""Domain repositories for data access."""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# Import models from their respective packages
from backend.etl.transform.models.company import Company
from backend.etl.transform.models.industry import Industry
from backend.etl.transform.models.sub_sector import SubSector
from backend.etl.transform.models.analytics import FinancialMetrics

class CompanyRepository(ABC):
    """Repository for company data access operations."""
    
    @abstractmethod
    def get_all_companies(self) -> List[Company]:
        """Retrieve all companies."""
        pass
    
    @abstractmethod
    def get_companies_by_sector(self, sector: str) -> List[Company]:
        """Retrieve companies by sector."""
        pass
    
    @abstractmethod
    def get_companies_by_sub_sector(self, sub_sector: str) -> List[Company]:
        """Retrieve companies by sub-sector."""
        pass

    @abstractmethod
    def save_companies(self, companies: List[Company]) -> None:
        """Save company information."""
        pass

class SectorRepository(ABC):
    """Repository for sector data access operations."""
    
    @abstractmethod
    def get_all_sectors(self) -> List[str]:
        """Retrieve all sectors."""
        pass
    
    @abstractmethod
    def get_sector_metrics(self, sector: str) -> Dict[str, Any]:
        """Retrieve metrics for a specific sector."""
        pass
    
    @abstractmethod
    def save_sector_metrics(self, sector: str, metrics: Dict[str, Any]) -> None:
        """Save metrics for a sector."""
        pass

class SubSectorRepository(ABC):
    """Repository for sub-sector data access operations."""
    
    @abstractmethod
    def get_all_sub_sectors(self) -> List[str]:
        """Retrieve all sub-sectors."""
        pass
    
    @abstractmethod
    def get_sub_sectors_by_sector(self, sector: str) -> List[str]:
        """Retrieve sub-sectors for a specific sector."""
        pass
    
    @abstractmethod
    def get_sub_sector_metrics(self, sub_sector: str) -> Dict[str, Any]:
        """Retrieve metrics for a specific sub-sector."""
        pass
    
    @abstractmethod
    def save_sub_sector_metrics(self, sub_sector: str, metrics: Dict[str, Any]) -> None:
        """Save metrics for a sub-sector."""
        pass

# Keep the old file as a reference for backward compatibility
from .repositories import CompanyRepository as LegacyCompanyRepository

__all__ = [
    'CompanyRepository', 
    'SectorRepository', 
    'SubSectorRepository',
    'LegacyCompanyRepository'  # For backward compatibility
]
