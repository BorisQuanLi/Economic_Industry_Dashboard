"""
Query Helper Utilities

This module provides utility functions for database queries.
"""

import logging
from typing import List, Dict, Any, Tuple, Optional

logger = logging.getLogger(__name__)

def build_where_clause(conditions: Dict[str, Any]) -> Tuple[str, List[Any]]:
    """
    Build a SQL WHERE clause from conditions.
    
    Args:
        conditions: Dictionary of column names and values
        
    Returns:
        Tuple of (WHERE clause string, parameter list)
    """
    if not conditions:
        return "", []
        
    clauses = []
    params = []
    
    for column, value in conditions.items():
        if value is None:
            clauses.append(f"{column} IS NULL")
        elif isinstance(value, (list, tuple)):
            placeholders = ", ".join(["%s"] * len(value))
            clauses.append(f"{column} IN ({placeholders})")
            params.extend(value)
        else:
            clauses.append(f"{column} = %s")
            params.append(value)
    
    where_clause = " AND ".join(clauses)
    return f"WHERE {where_clause}", params

def build_order_by_clause(order_by: Optional[str] = None, direction: str = "ASC") -> str:
    """
    Build a SQL ORDER BY clause.
    
    Args:
        order_by: Column to order by
        direction: Sort direction ("ASC" or "DESC")
        
    Returns:
        ORDER BY clause string
    """
    if not order_by:
        return ""
        
    # Sanitize direction
    direction = direction.upper()
    if direction not in ("ASC", "DESC"):
        direction = "ASC"
        
    return f"ORDER BY {order_by} {direction}"

def build_pagination_clause(limit: Optional[int] = None, offset: Optional[int] = None) -> Tuple[str, List[Any]]:
    """
    Build a SQL pagination clause.
    
    Args:
        limit: Maximum number of records to return
        offset: Number of records to skip
        
    Returns:
        Tuple of (pagination clause string, parameter list)
    """
    clauses = []
    params = []
    
    if limit is not None:
        clauses.append("LIMIT %s")
        params.append(limit)
        
    if offset is not None:
        clauses.append("OFFSET %s")
        params.append(offset)
        
    return " ".join(clauses), params

def format_date_range(start_date: Optional[str] = None, end_date: Optional[str] = None) -> Tuple[str, List[Any]]:
    """
    Format a date range for SQL queries.
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
        
    Returns:
        Tuple of (date range clause string, parameter list)
    """
    clauses = []
    params = []
    
    if start_date:
        clauses.append("date >= %s")
        params.append(start_date)
        
    if end_date:
        clauses.append("date <= %s")
        params.append(end_date)
        
    if clauses:
        return f"WHERE {' AND '.join(clauses)}", params
    
    return "", []

def build_time_filter(table_alias: str, time_period: str) -> str:
    """
    Build a SQL time filter clause for common time periods.
    
    Args:
        table_alias: The table alias to use in the query (e.g., 'qr' for quarterly_reports)
        time_period: The time period to filter for ('quarterly', 'annual', 'monthly', etc.)
        
    Returns:
        A SQL clause string
    """
    time_filters = {
        'quarterly': f"AND {table_alias}.date >= NOW() - INTERVAL '4 quarters'",
        'annual': f"AND {table_alias}.date >= NOW() - INTERVAL '4 years'",
        'ytd': f"AND {table_alias}.date >= DATE_TRUNC('year', NOW())",
        'monthly': f"AND {table_alias}.date >= NOW() - INTERVAL '12 months'",
        '5year': f"AND {table_alias}.date >= NOW() - INTERVAL '5 years'"
    }
    
    return time_filters.get(time_period, "")

def execute_safe_query(cursor, query: str, params: Tuple) -> Optional[List[Dict[str, Any]]]:
    """
    Execute a query safely, handling exceptions and returning results as dictionaries.
    
    Args:
        cursor: Database cursor
        query: SQL query string
        params: Query parameters
        
    Returns:
        List of result dictionaries or None on error
    """
    try:
        cursor.execute(query, params)
        return cursor.fetchall()
    except Exception as e:
        logger.error(f"Query execution error: {str(e)}")
        logger.debug(f"Failed query: {query} with params {params}")
        return None

def get_entity_by_id(cursor, table: str, id_value: int) -> Optional[Dict[str, Any]]:
    """
    Get an entity from a table by its ID.
    
    Args:
        cursor: Database cursor
        table: Table name
        id_value: ID value to look for
        
    Returns:
        Dictionary with entity data or None if not found
    """
    try:
        cursor.execute(f"SELECT * FROM {table} WHERE id = %s", (id_value,))
        return cursor.fetchone()
    except Exception as e:
        logger.error(f"Error fetching {table} with ID {id_value}: {str(e)}")
        return None
