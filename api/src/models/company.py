from api.src.db import db
import api.src.models as models


class Company:
    __table__ = "companies"
    columns = ['id', 'name', 'ticker', 'sub_industry_id', 'number_of_employees', 'HQ_state', 'country', 'year_founded']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f'{key} not in {self.columns}'
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_stock_ticker(self, stock_ticker, cursor):
        ticker_query = """SELECT * FROM companies WHERE ticker = %s;"""
        cursor.execute(ticker_query, (stock_ticker,))
        company_record = cursor.fetchone()
        return db.build_from_record(models.Company, company_record)

    @classmethod
    def find_by_company_id(self, company_id, cursor):
        sql_query = f"""SELECT * FROM {self.__table__}
                        WHERE id = %s;"""
        cursor.execute(sql_query, (company_id,))
        record = cursor.fetchone()
        return build_from_record(models.Company, record)

    def sub_industry(self, cursor):
        sql_query = f"""SELECT * FROM sub_industries 
                    WHEER sub_industries.id = %s;
                    """
        cursor.execute(sql_query, (self.sub_industry_id,))
        return db.build_from_record(models.SubIndustry, cursor.fetchone())
    
    def price_pe(self, cursor):
        pass

    def quarterly_reports(self, cursor):
        sql_query = f"""SELECT * FROM quarterly_reports
                    WHERE quarterly_reports.company_id = %s;"""
        cursor.execute(sql_query, (self.id,))
        records = cursor.fetchall()
        return db.build_from_records(models.QuarterlyReport, records) 
    
    def search_quarterly_report_by_ticker(self, ticker_params, cursor):
        pass
        ticker = ticker_params.values()[0]
        company = find_by_stock_ticker(ticker)
        # check if company is a Company object?
        # company_id = company.
        return   quarterly_report()


    