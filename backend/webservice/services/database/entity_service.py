"""
Entity Service

This module provides a service for entity-related database operations.
"""

import logging
from typing import List, Dict, Any, Optional
from .base_service import BaseDatabaseService

logger = logging.getLogger(__name__)

class EntityService(BaseDatabaseService):
    """Service for entity-related database operations."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    def get_sectors(self) -> List[Dict[str, Any]]:
        """
        Get all sectors.
        
        Returns:
            List of sector dictionaries
        """
        query = """
            SELECT id, name, description
            FROM sectors
            ORDER BY name
        """
        return self.fetch_records(query)
    
    def get_sector_by_id(self, sector_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a sector by ID.
        
        Args:
            sector_id: Sector ID
            
        Returns:
            Sector dictionary or None if not found
        """
        query = """
            SELECT id, name, description
            FROM sectors
            WHERE id = %s
        """
        return self.fetch_one(query, (sector_id,))
    
    def get_companies(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get all companies with pagination.
        
        Args:
            limit: Maximum number of companies to return
            offset: Number of companies to skip
            
        Returns:
            List of company dictionaries
        """
        query = """
            SELECT id, ticker, name, sector_id, sub_industry_id
            FROM companies
            ORDER BY name
            LIMIT %s OFFSET %s
        """
        return self.fetch_records(query, (limit, offset))
    
    def get_companies_by_sector(self, sector_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get companies in a sector with pagination.
        
        Args:
            sector_id: Sector ID
            limit: Maximum number of companies to return
            offset: Number of companies to skip
            
        Returns:
            List of company dictionaries
        """
        query = """
            SELECT id, ticker, name, sector_id, sub_industry_id
            FROM companies
            WHERE sector_id = %s
            ORDER BY name
            LIMIT %s OFFSET %s
        """
        return self.fetch_records(query, (sector_id, limit, offset))
    
    def get_company_by_ticker(self, ticker: str) -> Optional[Dict[str, Any]]:
        """
        Get a company by ticker symbol.
        
        Args:
            ticker: Company ticker symbol
            
        Returns:
            Company dictionary or None if not found
        """
        query = """
            SELECT id, ticker, name, sector_id, sub_industry_id
            FROM companies
            WHERE ticker = %s
        """
        return self.fetch_one(query, (ticker,))
    
    # For development/testing - provide mock data if database is not available
    
    def get_mock_sectors(self) -> List[Dict[str, Any]]:
        """Get mock sectors for development."""
        return [
            {"id": 1, "name": "Technology", "description": "Technology companies"},
            {"id": 2, "name": "Healthcare", "description": "Healthcare companies"},
            {"id": 3, "name": "Finance", "description": "Financial services companies"},
        ]
    
    def get_mock_companies(self) -> List[Dict[str, Any]]:
        """Get mock companies for development."""
        return [
            {"id": 1, "ticker": "AAPL", "name": "Apple Inc.", "sector_id": 1},
            {"id": 2, "ticker": "MSFT", "name": "Microsoft Corporation", "sector_id": 1},
            {"id": 3, "ticker": "JNJ", "name": "Johnson & Johnson", "sector_id": 2},
            {"id": 4, "ticker": "JPM", "name": "JPMorgan Chase & Co.", "sector_id": 3},
        ]
