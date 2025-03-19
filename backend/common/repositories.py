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

class CompanyRepository:
    """
    Repository for Company data access.
    
    This class is needed for backward compatibility with the LegacyCompanyRepository import
    in the etl/load/data_persistence/data_repositories.py file.
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize with database connection.
        
        Args:
            db_connection: Database connection object
        """
        self.db_connection = db_connection
    
    def get_all_companies(self):
        """
        Retrieve all companies from the database.
        
        Returns:
            list: List of company objects
        """
        # Implementation would query the database and return results
        return []
    
    def get_company_by_id(self, company_id):
        """
        Retrieve a company by its ID.
        
        Args:
            company_id: Unique identifier for the company
            
        Returns:
            dict: Company data or None if not found
        """
        # Implementation would query the database for a specific company
        return None
    
    def get_companies_by_sector(self, sector):
        """
        Retrieve all companies in a specific sector.
        
        Args:
            sector: Sector name
            
        Returns:
            list: List of companies in the sector
        """
        # Implementation would query the database for companies in a sector
        return []
    
    def get_companies_by_sub_sector(self, sub_sector):
        """
        Retrieve all companies in a specific sub-sector.
        
        Args:
            sub_sector: Sub-sector name
            
        Returns:
            list: List of companies in the sub-sector
        """
        # Implementation would query the database for companies in a sub-sector
        return []
    
    def save_company(self, company_data):
        """
        Save company data to the database.
        
        Args:
            company_data: Company information to save
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Implementation would save company data to the database
        return True
    
    def update_company(self, company_id, company_data):
        """
        Update existing company data.
        
        Args:
            company_id: Company ID to update
            company_data: Updated company information
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Implementation would update company data in the database
        return True
    
    def delete_company(self, company_id):
        """
        Delete a company from the database.
        
        Args:
            company_id: ID of the company to delete
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Implementation would delete a company from the database
        return True

__all__ = ['DataRepository', 'ExtractRepository', 'TransformRepository', 'LoadRepository', 'CompanyRepository']
