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
