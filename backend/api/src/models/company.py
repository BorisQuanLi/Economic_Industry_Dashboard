from api.src.db import db
import api.src.models as models
from api.src.models.queries.sql_query_strings import companies_within_sub_industry_str
from api.src.models.queries.query_company_financials_price_pe_history import Mixin as MixinCompanyFinancialsPricePE

class Company(MixinCompanyFinancialsPricePE):
    __table__ = "companies"
    columns = ['id', 'name', 'ticker', 'sub_industry_id', 'year_founded', 'number_of_employees', 'HQ_state']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f'{key} not in {self.columns}'
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_stock_ticker(self, stock_ticker:str, cursor):
        """
        returns a Company object, with values in all the fields, based on its ticker.
        """
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
        return db.build_from_record(models.Company, record)

    @classmethod
    def to_company_financials_history_json(self, sub_industry_name, cursor):
        # return in json format the financials and stock price, price-earnings-ratios of all the companies in a sub_industry
        company_names = MixinCompanyFinancialsPricePE.get_all_company_names_in_sub_industry(sub_industry_name, cursor)
        companies_quarterly_financials_dict = {}
        for company_name in company_names:
            companies_quarterly_financials_dict[company_name] = to_quarterly_financials_json(self, company_name, cursor)

    @classmethod
    def to_quarterly_financials_json(self, company_name, cursor):
        quarterly_reports_prices_pe_json = self.__dict__
        quarterly_reports_obj = self.get_company_quarterly_financials(self, company_name, cursor)
        quarterly_reports_prices_pe_json['Quarterly_financials'] = [report_obj.__dict__ for report_obj in quarterly_reports_obj]
        prices_pe_obj = self.get_company_quarterly_prices_pe(self, company_name, cursor)
        quarterly_reports_prices_pe_json['Closing_prices_and_P/E_ratio'] = [
                                                    price_pe_obj.__dict__ for price_pe_obj in prices_pe_obj]
        return quarterly_reports_prices_pe_json

    @classmethod
    def get_company_quarterly_financials(self, company_name, cursor):
        sql_str = f"""
                    SELECT quarterly_reports.* 
                    FROM quarterly_reports JOIN {sefl.__table__}
                    ON quarterly_reports.company_id = {sefl.__table__}.id
                    WHERE {sefl.__table__}.company_name = %s;        
                    """
        cursor.execute(sql_str, (company_name,))
        records = cursor.fetechall()
        return db.build_from_records(models.QuarterlyReport, records)

    @classmethod
    def get_company_quarterly_prices_pe(self, company_name, cursor):
        sql_str = f"""
                    SELECT prices_pe.* 
                    FROM prices_pe JOIN {sefl.__table__}
                    ON prices_pe.company_id = {sefl.__table__}.id
                    WHERE {sefl.__table__}.company_name = %s;        
                    """
        cursor.execute(sql_str, (company_name,))
        records = cursor.fetechall()
        return db.build_from_records(models.QuarterlyReport, records)

