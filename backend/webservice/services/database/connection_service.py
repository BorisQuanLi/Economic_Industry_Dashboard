"""
Database Connection Service

This module provides a service for managing database connections.
"""

import logging
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Any, Optional, Dict
import os

logger = logging.getLogger(__name__)

class ConnectionService:
    """Service for managing database connections."""
    
    def __init__(self):
        """Initialize the connection service."""
        self._config = self._get_config()
    
    def _get_config(self) -> Dict[str, Any]:
        """Get database configuration."""
        try:
            # First try to import from config module
            try:
                from ...config.settings import DB_CONFIG
                return DB_CONFIG
            except ImportError:
                # If config module not found, try environment variables
                logger.warning("Could not import DB_CONFIG, trying environment variables")
                return {
                    'host': os.environ.get('DB_HOST', 'localhost'),
                    'port': int(os.environ.get('DB_PORT', 5432)),
                    'database': os.environ.get('DB_NAME', 'economic_dashboard'),
                    'user': os.environ.get('DB_USER', 'postgres'),
                    'password': os.environ.get('DB_PASSWORD', 'postgres'),
                }
        except Exception as e:
            # If all else fails, use hardcoded defaults
            logger.warning(f"Error getting configuration: {str(e)}, using defaults")
            return {
                'host': 'localhost',
                'port': 5432,
                'database': 'economic_dashboard',
                'user': 'postgres',
                'password': 'postgres',
            }
    
    def get_connection(self) -> Optional[Any]:
        """
        Get a database connection.
        
        Returns:
            psycopg2.connection or None if connection fails
        """
        try:
            conn = psycopg2.connect(
                host=self._config.get('host', 'localhost'),
                port=self._config.get('port', 5432),
                database=self._config.get('database', 'economic_dashboard'),
                user=self._config.get('user', 'postgres'),
                password=self._config.get('password', 'postgres'),
            )
            return conn
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            return None
    
    def get_cursor(self, conn, cursor_factory=RealDictCursor):
        """
        Get a database cursor.
        
        Args:
            conn: Database connection
            cursor_factory: Cursor factory class
            
        Returns:
            Database cursor or None if conn is None
        """
        if conn:
            return conn.cursor(cursor_factory=cursor_factory)
        return None
    
    def close_connection(self, conn):
        """
        Close a database connection.
        
        Args:
            conn: Database connection to close
        """
        if conn:
            try:
                conn.close()
                logger.debug("Database connection closed")
            except Exception as e:
                logger.error(f"Error closing database connection: {str(e)}")
