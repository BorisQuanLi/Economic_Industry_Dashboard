
import api.src.db as db
from flask import request

def financial_performance_query_tools():
    conn = db.get_db()
    cursor = conn.cursor()
    params = dict(request.args)
    financial_indicator = params.get('financial_indicator', 0)
    return conn, cursor, financial_indicator

def sub_industry_performance_query_tools():
    conn = db.get_db()
    cursor = conn.cursor()
    params = dict(request.args)
    sector_name = params.get('sector_name', 0)
    financial_indicator = params.get('financial_indicator', 0)
    return conn, cursor, sector_name, financial_indicator
