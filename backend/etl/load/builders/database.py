"""Database loader implementations."""
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from backend.etl.load.data_persistence.base_database_repository import DatabaseRepository  # Updated import path

class DatabaseLoader(DatabaseRepository):
    """Database loader with session management."""
    
    @contextmanager
    def get_bulk_load_session(self) -> Generator[Session, None, None]:
        """Get session optimized for bulk loading."""
        session = self.SessionLocal()
        session.bulk_insert_mappings = True
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

"""Database builder for ETL load process."""

from etl.load.db.connection import get_db_connection

class DatabaseBuilder:
    """Builds database structures and loads data"""
    
    def __init__(self, connection=None):
        """Initialize database builder with optional connection"""
        self.connection = connection or get_db_connection()
        
    def build_tables(self, schema=None):
        """Build database tables from schema"""
        if not schema:
            return False
        
        try:
            cursor = self.connection.cursor()
            cursor.execute(schema)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error building tables: {e}")
            return False
