"""
Web Service Components

This package contains service components specific to the web application.
These services focus on web-specific functionality while delegating
data operations to the data services package.
"""

from backend.data.services import get_data_services

__all__ = ['get_data_services']
