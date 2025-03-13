"""Industry sector analysis and data access."""
from abc import ABC, abstractmethod
from typing import List, Dict
from .models import Company, SectorMetrics, SubSectorMetrics

class IndustryAnalyzer(ABC):
    """Analyzes industry sectors, sub-sectors, and companies."""
    
    @abstractmethod
    def get_sector_breakdown(self) -> Dict[str, List[str]]:
        """Get sectors and their sub-sectors."""
        pass
    
    @abstractmethod
    def get_subsector_companies(self, sector: str, subsector: str) -> List[Company]:
        """Get companies in a specific sub-sector."""
        pass

    @abstractmethod
    def get_sector_metrics(self, sector: str) -> SectorMetrics:
        """Get aggregated metrics for an entire sector."""
        pass
    
    @abstractmethod
    def get_subsector_metrics(self, sector: str, subsector: str) -> SubSectorMetrics:
        """Get aggregated metrics for a sub-sector."""
        pass

    @abstractmethod
    def save_sector_data(self, sector: str, companies: List[Company]) -> None:
        """Save sector and company data."""
        pass
