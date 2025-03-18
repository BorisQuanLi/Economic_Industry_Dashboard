from dataclasses import dataclass
from etl.load.db import connection as db
from etl.transform import models

class IndustryMetrics:
    """Class for industry-level metrics and analytics."""
    __table__ = 'industry_metrics'
    columns = ['id', 'name', 'sector_id', 'company_count', 'avg_pe_ratio', 'median_pe_ratio', 
               'market_cap_total', 'revenue_total', 'last_updated']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise ValueError(f"{key} not in {self.columns}")
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_sector_id(cls, sector_id, cursor):
        """Find all industry metrics by sector ID."""
        sql_str = f"""SELECT * FROM {cls.__table__}
                      WHERE sector_id = %s;"""
        cursor.execute(sql_str, (sector_id,))
        records = cursor.fetchall()
        return db.build_from_records(cls, records)

    @classmethod
    def find_all(cls, cursor):
        """Find all industry metrics."""
        sql_str = f"""SELECT * FROM {cls.__table__};"""
        cursor.execute(sql_str)
        records = cursor.fetchall()
        return db.build_from_records(cls, records)

@dataclass
class SectorMetrics:
    sector: str
    revenue: float
    cogs: float
    gross_profit: float
    randd: float
    sga: float
    operating_income: float
    interest_expense: float
    income_tax: float
    net_income: float


@dataclass
class SubSectorMetrics:
    sub_sector: str
    revenue: float
    cogs: float
    gross_profit: float
    randd: float
    sga: float
    operating_income: float
    interest_expense: float
    income_tax: float
    net_income: float
