"""Common imports and utilities used across the application."""

import os
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional
import json
import logging
from backend.etl.load.db import connection

# Setup logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def setup_project_path():
    """Add project root to Python path"""
    project_root = Path(__file__).parent.parent.parent
    if str(project_root) not in sys.path:
        sys.path.append(str(project_root))

def get_environment() -> str:
    """Get current environment"""
    return os.getenv('APP_ENV', 'local')

def financial_performance_query_tools():
    """
    Get connection, cursor, and financial indicator for querying
    
    Returns:
        tuple: (connection, cursor, financial_indicator)
    """
    try:
        conn = connection.get_connection()
        cursor = connection.get_cursor(conn) if conn else None
        financial_indicator = 'revenue'  # Default value
        
        return conn, cursor, financial_indicator
    except Exception as e:
        logger.error(f"Error in financial_performance_query_tools: {str(e)}")
        return None, None, 'revenue'
