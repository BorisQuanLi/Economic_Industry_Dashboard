"""
Base Database Service

This module provides a base class for database services.
"""

import logging
from typing import List, Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class BaseDatabaseService:
    """Base class for database services."""
    
    def __init__(self):
        """Initialize the base database service."""
        self._connection = None
    
    def connect(self) -> bool:
        """
        Establish a database connection.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            # Import here to avoid circular imports
            from .connection_service import ConnectionService
            connection_service = ConnectionService()
            self._connection = connection_service.get_connection()
            return self._connection is not None
        except Exception as e:
            logger.error(f"Error connecting to database: {str(e)}")
            return False
    
    def disconnect(self) -> bool:
        """
        Close the database connection.
        
        Returns:
            bool: True if disconnection successful, False otherwise
        """
        try:
            if self._connection:
                # Import here to avoid circular imports
                from .connection_service import ConnectionService
                connection_service = ConnectionService()
                connection_service.close_connection(self._connection)
                self._connection = None
            return True
        except Exception as e:
            logger.error(f"Error disconnecting from database: {str(e)}")
            return False
    
    def execute_query(self, query: str, params: Optional[Tuple] = None) -> bool:
        """
        Execute a database query.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            bool: True if query executed successfully, False otherwise
        """
        try:
            if not self._connection and not self.connect():
                return False
                
            cursor = self._connection.cursor()
            cursor.execute(query, params)
            self._connection.commit()
            cursor.close()
            return True
        except Exception as e:
            logger.error(f"Error executing query: {str(e)}")
            return False
    
    def fetch_records(self, query: str, params: Optional[Tuple] = None) -> List[Dict[str, Any]]:
        """
        Fetch records from the database.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            List of record dictionaries
        """
        try:
            if not self._connection and not self.connect():
                return []
                
            cursor = self._connection.cursor(dictionary=True)
            cursor.execute(query, params)
            records = cursor.fetchall()
            cursor.close()
            return records if records else []
        except Exception as e:
            logger.error(f"Error fetching records: {str(e)}")
            return []
    
    def fetch_one(self, query: str, params: Optional[Tuple] = None) -> Optional[Dict[str, Any]]:
        """
        Fetch a single record from the database.
        
        Args:
            query: SQL query string
            params: Optional query parameters
            
        Returns:
            Record dictionary or None
        """
        try:
            if not self._connection and not self.connect():
                return None
                
            cursor = self._connection.cursor(dictionary=True)
            cursor.execute(query, params)
            record = cursor.fetchone()
            cursor.close()
            return record
        except Exception as e:
            logger.error(f"Error fetching record: {str(e)}")
            return None
