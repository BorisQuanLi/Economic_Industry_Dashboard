"""Data access interfaces."""
from abc import ABC, abstractmethod
from typing import List
from .models import Company, FinancialMetrics

class CompanyRepository(ABC):
    @abstractmethod
    def get_all_sectors(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_companies_by_sector(self, sector: str) -> List[Company]:
        pass

    @abstractmethod
    def save_companies(self, companies: List[Company]) -> None:
        pass
