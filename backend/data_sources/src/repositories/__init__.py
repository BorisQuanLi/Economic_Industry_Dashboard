"""Repository implementations for data access."""

from .base import DataRepository
from .local_postgres import LocalPostgresRepository
from .aws import AWSRepository

__all__ = ['DataRepository', 'LocalPostgresRepository', 'AWSRepository']
