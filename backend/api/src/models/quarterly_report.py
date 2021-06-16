from api.src.db import db
from api.src import models

class QuarterlyReport:
    __table__ = 'quarterly_reports'
    columns = ['id', 'date', 'company_id', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f'{key} not in {self.columns}'
        for k,v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_company_id(self, company_id, cursor):
        sql_str = f"""SELECT * FROM {self.__table__}
                        WHERE company_id = %s;"""
        cursor.execute(sql_str, (company_id,))
        records = cursor.fetchall()
        return db.build_from_records(self, records)

    @classmethod
    def find_quarterly_reports_by_ticker(self, ticker, cursor):
        sql_query = f"""SELECT * FROM quarterly_reports
                        JOIN companies
                        ON companies.id = quarterly_reports.company_id
                        WHERE companies.ticker = %s;"""
        cursor.execute(sql_query, (ticker,))
        records = cursor.fetchall()
        return db.build_from_records(self, records)