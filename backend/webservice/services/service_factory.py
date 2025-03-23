"""
Service Factory

This module provides a factory for creating service instances.
"""

import logging
from typing import Dict, Any, Type

logger = logging.getLogger(__name__)

# Import services - handle possible import errors
try:
    from .database.query_service import QueryService
    from .database.connection_service import ConnectionService
    from .database.entity_service import EntityService
    from .industry_metrics.company_metrics import CompanyMetrics
    from .industry_metrics.sector_metrics import SectorMetrics
    from .industry_metrics.subindustry_metrics import SubindustryMetrics
    from .data_processing.data_processor import DataProcessor
except ImportError as e:
    logger.error(f"Error importing service modules: {str(e)}")
    # Create stub classes if needed
    class StubService:
        """Stub service that does nothing."""
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
            
    QueryService = ConnectionService = EntityService = StubService
    CompanyMetrics = SectorMetrics = SubindustryMetrics = StubService
    DataProcessor = StubService

class ServiceFactory:
    """Factory for creating and caching service instances."""
    
    _instances: Dict[str, Any] = {}
    
    @classmethod
    def get_query_service(cls) -> Any:
        """Get or create a QueryService instance."""
        return cls._get_service(QueryService)
    
    @classmethod
    def get_connection_service(cls) -> Any:
        """Get or create a ConnectionService instance."""
        return cls._get_service(ConnectionService)
    
    @classmethod
    def get_entity_service(cls) -> Any:
        """Get or create an EntityService instance."""
        return cls._get_service(EntityService)
    
    @classmethod
    def get_company_metrics(cls) -> Any:
        """Get or create a CompanyMetrics instance."""
        return cls._get_service(CompanyMetrics)
    
    @classmethod
    def get_sector_metrics(cls) -> Any:
        """Get or create a SectorMetrics instance."""
        return cls._get_service(SectorMetrics)
    
    @classmethod
    def get_subindustry_metrics(cls) -> Any:
        """Get or create a SubindustryMetrics instance."""
        return cls._get_service(SubindustryMetrics)
    
    @classmethod
    def get_data_processor(cls) -> Any:
        """Get or create a DataProcessor instance."""
        return cls._get_service(DataProcessor)
    
    @classmethod
    def _get_service(cls, service_class: Type) -> Any:
        """Get or create a service instance of the specified class."""
        service_name = service_class.__name__
        if service_name not in cls._instances:
            logger.debug(f"Creating new {service_name} instance")
            try:
                cls._instances[service_name] = service_class()
            except Exception as e:
                logger.error(f"Error creating {service_name}: {str(e)}")
                cls._instances[service_name] = None
        return cls._instances[service_name]
