"""Base model for company information."""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from backend.etl.load.db import connection as db

@dataclass
class CompanyInfo:
    id: int
    name: str
    ticker: str
    sub_industry_id: int
    year_founded: Optional[int]
    number_of_employees: Optional[int]
    HQ_state: Optional[str]
    
    columns = ['id', 'ticker', 'name', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state']
    
    def __init__(self, id=None, ticker=None, name=None, sub_industry_id=None, 
                 year_founded=None, number_of_employees=None, HQ_state=None):
        """Initialize a CompanyInfo instance."""
        self.id = id
        self.ticker = ticker
        self.name = name
        self.sub_industry_id = sub_industry_id
        self.year_founded = year_founded
        self.number_of_employees = number_of_employees
        self.HQ_state = HQ_state
    
    @classmethod
    def find_by_stock_ticker(cls, stock_ticker: str, cursor):
        """Returns a CompanyInfo object based on its ticker."""
        ticker_query = """SELECT * FROM companies WHERE ticker = %s;"""
        cursor.execute(ticker_query, (stock_ticker,))
        company_record = cursor.fetchone()
        return db.build_from_record(cls, company_record)

    @classmethod
    def find_by_company_id(cls, company_id: int, cursor):
        """Returns a CompanyInfo object based on its ID."""
        sql_query = """SELECT * FROM companies WHERE id = %s;"""
        cursor.execute(sql_query, (company_id,))
        record = cursor.fetchone()
        return db.build_from_record(cls, record)
        
    @classmethod
    def get_companies_in_sub_industry(cls, sub_industry_name: str, cursor) -> List[Dict[str, Any]]:
        """Get all companies in a sub-industry."""
        sql_query = """
            SELECT c.* FROM companies c
            JOIN sub_industries si ON c.sub_industry_id = si.id
            WHERE si.sub_industry_gics = %s;
        """
        cursor.execute(sql_query, (sub_industry_name,))
        return cursor.fetchall()
        
    @classmethod
    def get_companies_in_sector(cls, sector_name: str, cursor) -> List[Dict[str, Any]]:
        """Get all companies in a sector."""
        sql_query = """
            SELECT c.* FROM companies c
            JOIN sub_industries si ON c.sub_industry_id = si.id
            WHERE si.sector_gics = %s;
        """
        cursor.execute(sql_query, (sector_name,))
        return cursor.fetchall()