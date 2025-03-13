"""Database loader implementations."""
from abc import ABC, abstractmethod
from contextlib import contextmanager
from typing import Generator
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from ...repositories.base import DatabaseRepository

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
