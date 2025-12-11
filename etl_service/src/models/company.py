from etl_service.src.db import db
import etl_service.src.models as models
from etl_service.src.models.queries.sql_query_strings import companies_within_sub_sector_str, extract_single_financial_indicator
from etl_service.src.models.queries.query_company_price_pe_history import MixinCompanyPricePE
from etl_service.src.models.queries.query_company_financials_history import MixinCompanyFinancials


class Company(MixinCompanyPricePE, MixinCompanyFinancials): 
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
    def to_quarterly_financials_json(self, company_name, cursor):
        quarterly_reports = self.get_company_quarterly_financials(company_name, cursor)
        prices_pe = self.get_company_quarterly_prices_pe(company_name, cursor)
        
        # Create a dictionary for prices_pe for easier lookup
        prices_pe_dict = {(p.year, p.quarter): p for p in prices_pe}
        
        merged_data = []
        for report in quarterly_reports:
            price_pe_data = prices_pe_dict.get((report.year, report.quarter))
            if price_pe_data:
                merged_record = {**report.__dict__, **price_pe_data.__dict__}
                merged_data.append(merged_record)
        
        return merged_data

    @classmethod
    def get_company_quarterly_financials(self, company_name, cursor):
        sql_str = f"""
                    SELECT quarterly_reports.* 
                    FROM quarterly_reports JOIN {self.__table__}
                    ON quarterly_reports.company_id = {self.__table__}.id
                    WHERE {self.__table__}.name = %s;        
                    """
        cursor.execute(sql_str, (company_name,))
        records = cursor.fetchall()
        return db.build_from_records(models.QuarterlyReport, records)

    @classmethod
    def get_company_quarterly_prices_pe(self, company_name, cursor):
        sql_str = f"""
                    SELECT prices_pe.* 
                    FROM prices_pe JOIN {self.__table__}
                    ON prices_pe.company_id = {self.__table__}.id
                    WHERE {self.__table__}.name = %s;        
                    """
        cursor.execute(sql_str, (company_name,))
        records = cursor.fetchall()
        return db.build_from_records(models.PricePE, records)

    @classmethod
    def find_companies_quarterly_financials(self, sub_sector_name:str, financial_indicator:str, cursor):
        """
        Within each chosen sub_sector, calculate each company's chosen
        financial-statement item (revenue, net_profit, etc.) over the most recent 8
        quarters.

        Returns a list of dictionaries with the key being a list of attributes, incl. [sector_name,
        financial_indicator name, year, quarter], and their corresponding values stored in a list as 
        the dictionary value.
        """
        companies_quarterly_financials_json = self.to_all_companies_quarterly_financials_json(sub_sector_name, financial_indicator, cursor)
        single_financial_indicator_json = extract_single_financial_indicator(financial_indicator, companies_quarterly_financials_json)
        return single_financial_indicator_json

    @classmethod
    def to_all_companies_quarterly_financials_json(self, sub_sector_name, financial_indicator, cursor):
        company_names = self.get_all_company_names_in_sub_sector(sub_sector_name, cursor)
        avg_quarterly_financials_dict = {}
        for company_name in company_names:
            avg_quarterly_financials_dict[company_name] = self.to_quarterly_financials_json(company_name, cursor)
        return avg_quarterly_financials_dict

    @classmethod
    def find_company_quarterly_price_pe(self, sub_sector_name:str, financial_indicator:str, cursor):
        companies_quarterly_price_pe_json = self.to_all_companies_quarterly_price_pe_json(sub_sector_name, financial_indicator, cursor)
        single_financial_indicator_json = extract_single_financial_indicator(financial_indicator, companies_quarterly_price_pe_json)
        return single_financial_indicator_json

    @classmethod
    def to_all_companies_quarterly_price_pe_json(self, sub_sector_name, financial_indicator, cursor):
        company_names = self.get_all_company_names_in_sub_sector(sub_sector_name, cursor)
        avg_quarterly_price_pe_dict = {}
        for company_name in company_names:
            avg_quarterly_price_pe_dict[company_name] = self.to_quarterly_price_pe_json(company_name, cursor)
        return avg_quarterly_price_pe_dict

