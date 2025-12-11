# fastapi_backend/db_session.py
"""Database session dependency for FastAPI endpoints."""

from typing import Generator
import psycopg2

from settings import DB_USER, DB_PASS, DB_NAME, DB_HOST


def get_db_connection():
    """Create a new database connection."""
    conn = psycopg2.connect(
        host=DB_HOST,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn


def get_db_session() -> Generator:
    """FastAPI dependency that yields a DB cursor, then closes connection."""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        cursor.close()
        conn.close()
