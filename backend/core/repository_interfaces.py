"""Core repository interfaces for data access across the ETL pipeline.

This module is the canonical location for all repository interfaces.
The interfaces in common/repositories.py are deprecated and will be removed in a future version.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any

# Re-export the interfaces from common to maintain compatibility
from backend.common.repositories import (
    DataRepository, 
    ExtractRepository,
    TransformRepository, 
    LoadRepository
)

# Future interfaces should be defined here
class AnalyticsRepository(DataRepository):
    """Repository interface for analytics operations."""
    
    @abstractmethod
    def get_time_series(self, entity_id: str, metric: str, 
                        start_date: str, end_date: str) -> Dict[str, Any]:
        """Get time series data for a specific entity and metric."""
        pass

# Version 2.0 interfaces with improved design
class EntityRepository(ABC):
    """Next generation base repository interface for entity data access."""
    
    @abstractmethod
    def get_by_id(self, entity_id: str) -> Dict[str, Any]:
        """Get entity by ID."""
        pass
    
    @abstractmethod
    def save(self, entity_data: Dict[str, Any]) -> bool:
        """Save entity data."""
        pass

__all__ = [
    # Re-exported interfaces
    'DataRepository', 
    'ExtractRepository',
    'TransformRepository', 
    'LoadRepository',
    
    # New interfaces
    'AnalyticsRepository',
    'EntityRepository'
]
