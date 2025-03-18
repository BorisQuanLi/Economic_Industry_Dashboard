"""Test utilities for repository access.

Note: This file should import from the core implementation rather than duplicate definitions.
"""
# Import from the real implementation
from backend.etl.load.data_persistence.data_repositories import (
    CompanyRepository,
    SectorRepository,
    SubSectorRepository
)

# Import interfaces from the core implementation
from backend.core.repository_interfaces import (
    DataRepository,
    ExtractRepository,
    TransformRepository,
    LoadRepository
)

# Export only what's needed for tests
__all__ = [
    'CompanyRepository',
    'SectorRepository', 
    'SubSectorRepository',
    'DataRepository',
    'ExtractRepository',
    'TransformRepository',
    'LoadRepository'
]
