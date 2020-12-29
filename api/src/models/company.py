from api.src.db import db
import api.src.models as models

class Company:
    __table__ = "companies"
    columns = ['id', 'name', 'ticker', 'sub_industry_id', 'number_of_employees', 'HQs_state', 'country', 'year_founded']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f'{key} not in {self.columns}'
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_stock_ticker(self, stock_ticker, cursor):
        ticker_query = """SELECT * FROM companies WHERE stock_ticker = %s;"""
        cursor.execute(ticker_query, (stock_ticker,))
        company_record = cursor.fetchone()
        return db.build_from_record(models.Company, company_record)

    def sub_industry(self, cursor):
        sql_query = f"""SELECT * FROM sub_industries 
                    WHEER sub_industries.id = %s;
                    """
        cursor.execute(sql_query, (self.sub_industry_id,))
        return db.build_from_record(models.SubIndustry, cursor.fetchone())
    
    def price_pe(self, cursor):
        pass

    def quarterly_report(self, cursor):
        sql_query = f"""SELECT * FROM quarterly_reports
                    WHERE quarterly_reports.company_id = %s;"""
        cursor.execute(sql_query, (self.id,))
        records = cursor.fetchall()
        return db.build_from_records(models.QuarterlyReport, records) 
    def to_json(self, cursor):
        pass


    