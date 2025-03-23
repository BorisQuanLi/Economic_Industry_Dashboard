"""
ETL package initialization

This package provides ETL (Extract, Transform, Load) functionality for the Economic Industry Dashboard.
"""

# Import key modules for easier access
from .transform.models.industry.sector import SubIndustry
from .transform.adapters.imports import financial_performance_query_tools
from .load.db import connection

__all__ = [
    'SubIndustry',
    'financial_performance_query_tools',
    'connection'
]
