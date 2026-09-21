# fastapi_backend/db_session.py
"""Database session dependency for FastAPI endpoints."""

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


def get_db_session():
    """
    FastAPI dependency that provides a database connection and handles cleanup.
    Usage: conn = Depends(get_db_session)
    """
    conn = None
    try:
        conn = get_db_connection()
        yield conn
    except Exception:
        yield None
    finally:
        if conn is not None:
            conn.close()
