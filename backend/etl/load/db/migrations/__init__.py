"""
Database Migrations Package

DEPRECATION NOTICE: This package is deprecated and will be removed in a future version.
The migration scripts have been moved to backend.webservice.database.migrations.
"""

import warnings
import os

warnings.warn(
    "This package is deprecated. Use backend.webservice.database.migrations instead.",
    DeprecationWarning,
    stacklevel=2
)

# Re-export the CREATE_TABLES_SQL for backward compatibility
from backend.webservice.database.migrations.schema import CREATE_TABLES_SQL
