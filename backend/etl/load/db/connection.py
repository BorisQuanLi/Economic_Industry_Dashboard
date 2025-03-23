"""
Flask Database Connection Adapter

This module serves as an adapter between Flask application context
and the LocalPostgresRepository implementation. It:

1. Manages database connections within Flask's application context
2. Provides utility functions for domain object construction
3. Exposes helper methods for common database operations

Design Note:
-----------
This adapter delegates actual database operations to the repository classes in
etl/load/data_persistence/ to avoid duplication of database connection logic.
"""

from flask import current_app, g
import psycopg2
from datetime import datetime, timedelta
from backend.etl.config import get_config
from backend.etl.load.data_persistence.local_postgres import LocalPostgresRepository

def get_db():
    """
    Get or create database connection in Flask application context.
    
    Returns:
        psycopg2.connection: Database connection
    """
    if "db" not in g:
        config = get_config()
        # Create repository
        repo = LocalPostgresRepository(db_config=config.db)
        # Store both the repository and its connection
        g.db_repo = repo
        g.db = repo._connection
    return g.db

def get_db_repo():
    """
    Get or create LocalPostgresRepository in Flask application context.
    
    Returns:
        LocalPostgresRepository: Repository for database operations
    """
    if "db_repo" not in g:
        get_db()  # This will create both db and db_repo
    return g.db_repo

def close_db(e=None):
    """Close database connection when Flask application context ends."""
    db_repo = g.pop("db_repo", None)
    if db_repo is not None:
        db_repo.close()
    # The connection will be closed by the repository, but we'll also remove it from g
    g.pop("db", None)

# Domain object utilities
def build_from_record(Class, record):
    """Build a domain object from a database record."""
    if not record: return None
    attr = dict(zip(Class.columns, record))
    obj = Class()
    obj.__dict__ = attr
    return obj

def build_from_records(Class, records):
    """Build multiple domain objects from database records."""
    return [build_from_record(Class, record) for record in records]

# Delegate repository operations
def find_all(Class, cursor):
    """Find all records for a domain class."""
    sql_str = f"SELECT * FROM {Class.__table__}"
    cursor.execute(sql_str)
    records = cursor.fetchall()
    return [build_from_record(Class, record) for record in records]

def find(Class, id, cursor):
    """Find a record by ID."""
    sql_str = f"SELECT * FROM {Class.__table__} WHERE id = %s"
    cursor.execute(sql_str, (id,))
    record = cursor.fetchone()
    return build_from_record(Class, record)

# Business domain queries 
# These should eventually move to specialized query repositories

def find_company_objs_by_sector(Class, sector_name, cursor):
    """Find companies by sector name."""
    sql_str = f"""SELECT * FROM companies
                    JOIN sub_industries 
                    ON companies.sub_industry_id::INT = sub_industries.id
                    WHERE sub_industries.sector_gics = %s;
                """
    cursor.execute(sql_str, (sector_name,))
    companies_records = cursor.fetchall()
    companies_objs = build_from_records(Class, companies_records)
    return companies_objs
    
def find_companies_by_sub_industry_name(Class, sub_industry_name, cursor):
    """
    params  Class: models.Company
            sub_industry_name: value of the sub_industry_gics column in the sub_industries table

    returns Company objects of all the companies in the same sub_industry
    """
    sql_str = f"""SELECT companies.* FROM companies 
                  JOIN sub_industries
                  ON companies.sub_industry_id::INTEGER = sub_industries.id
                  WHERE sub_industries.sub_industry_gics = %s;
                """
    cursor.execute(sql_str, (sub_industry_name,))
    records = cursor.fetchall()
    return build_from_records(Class, records)

def find_by_ticker(Class, ticker_symbol, cursor):
    search_str = f"""SELECT * FROM {Class.__table__} WHERE ticker = %s;"""
    cursor.execute(search_str, (ticker_symbol,))
    record = cursor.fetchone()
    return build_from_record(Class, record)

def find_company_by_name(company_name, cursor):
    search_str = "SELECT * From companies where name = %$;"
    cursor.execute(search_str, (company_name,))
    record = cursor.fetchone()
    return build_from_record(record)

def find_company_by_ticker(Class, ticker_symbol, cursor):
    sql_str = f"""SELECT * FROM companies
                    WHERE ticker = %s;"""
    cursor.execute(sql_str, (ticker_symbol,))
    record = cursor.fetchone()
    return build_from_record(Class, record)

def values(obj):
    company_attrs = obj.__dict__
    return [company_attrs[attr] for attr in obj.columns if attr in company_attrs.keys()]

def keys(obj):
    company_attrs = obj.__dict__
    selected = [attr for attr in obj.columns if attr in company_attrs.keys()]
    return ', '.join(selected)

def drop_records(cursor, conn, table_name):
    cursor.execute(f"DELETE FROM {table_name};")
    conn.commit()

def drop_tables(table_names, cursor, conn):
    for table_name in table_names:
        drop_records(cursor, conn, table_name)

def drop_all_tables(conn, cursor):
    table_names = ['companies', 'sub_industries', 'quarterly_reports', 'prices_pe']
    drop_tables(table_names, cursor, conn)

def find_by_name(Class, name, cursor):
    query = f"""SELECT * FROM {Class.__table__} WHERE name = %s """
    cursor.execute(query, (name,))
    record =  cursor.fetchone()
    obj = build_from_record(Class, record)
    return obj

def find_or_create_by_name(Class, name, conn, cursor):
    obj = find_by_name(Class, name, cursor)
    if not obj:
        new_obj = Class()
        new_obj.name = name
        obj = save(new_obj, conn, cursor)
    return obj

def save(obj, conn, cursor):
    s_str = ', '.join(len(values(obj)) * ['%s'])
    company_str = f"""INSERT INTO {obj.__table__} ({keys(obj)}) VALUES ({s_str});"""
    try:
        cursor.execute(company_str, list(values(obj)))
        conn.commit()
        cursor.execute(f'SELECT * FROM {obj.__table__} ORDER BY id DESC LIMIT 1')
        record = cursor.fetchone()
        return build_from_record(type(obj), record)
    except psycopg2.errors.UniqueViolation as e:
        print(e)
        pass

def get_db_connection():
    """Get standalone database connection (non-Flask context)."""
    config = get_config()
    repo = LocalPostgresRepository(db_config=config.db)
    return repo._connection

"""
Database connection module for ETL processes.
"""
import logging
import psycopg2
from psycopg2.extras import RealDictCursor

logger = logging.getLogger(__name__)

def get_connection():
    """Get a database connection."""
    try:
        conn = psycopg2.connect(
            host="localhost",
            database="economic_dashboard",
            user="postgres",
            password="postgres"
        )
        return conn
    except Exception as e:
        logger.error(f"Error connecting to database: {str(e)}")
        return None

def get_cursor(conn, cursor_factory=RealDictCursor):
    """Get a database cursor from a connection."""
    if conn:
        return conn.cursor(cursor_factory=cursor_factory)
    return None

def close_connection(conn):
    """Close a database connection."""
    if conn:
        conn.close()


