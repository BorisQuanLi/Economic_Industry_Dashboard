from api.src.db import db
import api.src.models as models
from functools import reduce
from datetime import datetime
from collections import defaultdict
#  import api.src.models.find_avg_quarterly_financials_by_sub_industry

class SubIndustry:
    __table__ = "sub_industries"
    columns = ['id', 'sub_industry_GICS', 'sector_GICS']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f"{key} is not in columns {self.columns}"
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_sub_industry_name(self, sub_industry_name, cursor):
        sql_str = f"""SELECT * FROM {self.__table__}
                    WHERE sub_industry_GICS = %s"""
        cursor.execute(sql_str, (sub_industry_name,))
        record = cursor.fetchone()
        return db.build_from_record(SubIndustry, record)

    @classmethod
    def find_companies_by_sub_industry(self, sub_industry_id, cursor):
        """
        # a list of Company instances
        companies_list = db.build_from_records(models.Company, records)
        # passed to a Company method to calculate average financials, to be shown in Flask app only?
        # Or which ones are eye-cataching for front-end Streamlit presentation, other than company name,
        # ticker, stock price, p/e, number of employees, year founded?  
        return # object whose format can conform to streamlit for front-end presentation
        """

        sql_str = f"""SELECT companies.* FROM companies
                      JOIN sub_industries
                      ON sub_industries.id = companies.sub_industry_id
                      WHERE sub_industries.id = %s;
                    """
        cursor.execute(sql_str, (str(sub_industry_id),))
        records = cursor.fetchall() 
        return db.build_from_records(models.Company, records)
    
    ### find_avg_price_pe_by_sectors
    @classmethod
    def find_avg_price_pe_by_sectors(self, financial_item, cursor):
        sql_str = self.sector_price_pe_sql_query()
        cursor.execute(sql_str)
        records = cursor.fetchall()
        sector_record_dicts = self.unpack_sector_price_pe_records(records)
        uniform_length_sector_record_dicts = self.get_uniform_time_periods_dicts(sector_record_dicts, uniform_length=5) 
        return uniform_length_sector_record_dicts

    @classmethod
    def sector_price_pe_sql_query(self):
        sql_str = f"""  SELECT  sector_gics,
                                EXTRACT(year from date::DATE) as year,
                                EXTRACT(quarter from date::DATE) as quarter,
                                ROUND(AVG(closing_price)::NUMERIC, 2) as avg_closing_price,
                                ROUND(AVG(price_earnings_ratio)::NUMERIC, 2) as avg_pe_ratio           
                        FROM prices_pe
                        JOIN companies 
                        ON companies.id = prices_pe.company_id
                        JOIN sub_industries
                        ON companies.sub_industry_id::INT = sub_industries.id
                        GROUP BY sub_industries.sector_gics, year, quarter
                        ORDER BY year, quarter;
                    """
        return sql_str

    @classmethod
    def unpack_sector_price_pe_records(self, records):
        self.sector_records_dict = {}
        [self.unpack_sector_price_pe_record(record) for record in records]
        return self.sector_records_dict

    @classmethod
    def unpack_sector_price_pe_record(self, record):
        self.sector_name = record[0]
        if self.sector_name not in self.sector_records_dict:
            self.sector_records_dict[f'{self.sector_name}'] = {}
        self.year_quarter = self.unpack_year_quarter(record)
        self.sector_price_pe_dict = self.get_price_pe_dict(record)
        return self.sector_records_dict

    @classmethod
    def get_price_pe_dict(self, record):
        self.sector_records_dict[f'{self.sector_name}'][self.year_quarter] = {}
        quarter_price_pe_dict = self.sector_records_dict[f'{self.sector_name}'][self.year_quarter]
        quarter_price_pe_dict['avg_closing_price'] = record[3]
        quarter_price_pe_dict['avg_price_earnings_ratio'] = record[4]
        return self.sector_records_dict

    ### find_avg_quarterly_financials_by_sectors
    @classmethod
    def find_avg_quarterly_financials_by_sectors(self, cursor):
        sql_str = self.sector_quarterly_financials_sql_query()
        cursor.execute(sql_str)
        records = cursor.fetchall()
        sector_record_dicts = self.unpack_sector_quarterly_report_records(records)
        uniform_length_sector_record_dicts = self.get_uniform_time_periods_dicts(sector_record_dicts, uniform_length=5) 
        return uniform_length_sector_record_dicts

    @classmethod
    def sector_quarterly_financials_sql_query(self): 
        sql_str = f"""  SELECT  sector_gics,
                                EXTRACT(year from date::DATE) as year,
                                EXTRACT(quarter from date::DATE) as quarter,
                                ROUND(AVG(revenue)::NUMERIC, 2) as avg_revenue,
                                ROUND(AVG(net_income)::NUMERIC, 2) as avg_net_income,
                                ROUND(AVG(earnings_per_share)::NUMERIC, 2) as avg_earnings_per_share,
                                ROUND(AVG(profit_margin)::NUMERIC, 2) as avg_profit_margin              
                        FROM quarterly_reports
                        JOIN companies 
                        ON companies.id = quarterly_reports.company_id
                        JOIN sub_industries
                        ON companies.sub_industry_id::INT = sub_industries.id
                        GROUP BY sub_industries.sector_gics, year, quarter
                        ORDER BY year, quarter;
                    """
        return sql_str

    @classmethod
    def unpack_sector_quarterly_report_records(self, records):
        self.sector_records_dict = {}
        [self.unpack_sector_quarterly_report_record(record) for record in records]
        return self.sector_records_dict

    @classmethod
    def unpack_sector_quarterly_report_record(self, record):
        self.sector_name = record[0]
        if self.sector_name not in self.sector_records_dict:
            self.sector_records_dict[f'{self.sector_name}'] = {}
        self.year_quarter = self.unpack_year_quarter(record)
        self.sector_records_dict = self.get_quarter_financials_dict(record)
        return self.sector_records_dict

    @classmethod
    def unpack_year_quarter(self, record):
        year = str(int(record[1]))
        quarter = str(int(record[2]))
        year_quarter = int(f"{year}0{quarter}")
        return year_quarter

    @classmethod
    def get_quarter_financials_dict(self, record):
        self.sector_records_dict[f'{self.sector_name}'][self.year_quarter] = {}
        quarter_financials_dict = self.sector_records_dict[f'{self.sector_name}'][self.year_quarter]
        quarter_financials_dict['avg_revenue'] = record[3]
        quarter_financials_dict['avg_net_income'] = record[4]
        quarter_financials_dict['avg_earnings_per_share'] = record[5]
        quarter_financials_dict['avg_profit_margin'] = record[6]
        return self.sector_records_dict

    @classmethod
    def get_uniform_time_periods_dicts(self, dict_of_dicts, uniform_length=5):
        most_recent_quarters = self.get_most_recent_quarters(dict_of_dicts, uniform_length)
        for key, value in dict_of_dicts.items():
            dict_of_dicts[key] = {quarter:quarter_records for quarter, quarter_records in value.items()
                                                                        if quarter in most_recent_quarters}
        return dict_of_dicts
    
    @classmethod
    def get_most_recent_quarters(self, dict_of_dicts, uniform_length):
        most_recent_quarter = max([max(dict_of_dicts[sector].keys()) 
                                                for sector in dict_of_dicts.keys()])
        for quarterly_records in dict_of_dicts.values():
            # search for the quarterly_records list with ends with the most_recent_quarter
            if most_recent_quarter not in quarterly_records.keys(): continue
            else:
                most_recent_quarters = list(quarterly_records.keys())[-uniform_length:]
                break
        return most_recent_quarters

    ### find_avg_quarterly_financials_by_sub_industry
    @classmethod
    def find_avg_quarterly_financials_by_sub_industry(self, sector_name:str, financial_item:str, cursor):
        """
        Within each chosen sector, calculate each sub_industry's average value of a chosen
        financial-statement item (revenue, net_profit, etc.) over the most recent 
        quarters (5 in total based on the API calls to this project's data source.

        Returns a list of dictionaries with the key being a list of attributes, incl. [sector_name,
        financial_item name, year, quarter], and their corresponding values stored in a list as 
        the dictionary value.
        """
        self.sector_name = sector_name
        self.financial_item = financial_item
        records = self.get_records(sector_name, financial_item, cursor) 
        avg_financial_by_sub_industries_dict = self.store_records(records) 
        avg_financial_dict_with_uniform_length = self.get_uniform_time_periods_dicts(avg_financial_by_sub_industries_dict) 
        historical_financials_json_dict = self.to_historical_financials_json(sector_name, financial_item,
                                                                                    avg_financial_dict_with_uniform_length)
        return historical_financials_json_dict

    @classmethod
    def get_records(self, sector_name, financial_item, cursor): 
        sql_str = self.sql_sub_industries_query(financial_item)
        cursor.execute(sql_str, (sector_name,))
        records = cursor.fetchall()
        return records

    @classmethod
    def sql_sub_industries_query(self, financial_item):
        sql_str = f"""select {self.__table__}.id, {self.__table__}.sub_industry_gics,
                            ROUND(AVG({financial_item})::NUMERIC, 2) as Average,
                            EXTRACT(year from quarterly_reports.date::DATE) as year,
                            EXTRACT(quarter from quarterly_reports.date::DATE) as quarter
                        FROM quarterly_reports
                        JOIN companies ON quarterly_reports.company_id::INTEGER = companies.id
                        JOIN {self.__table__} ON {self.__table__}.id = companies.sub_industry_id::INTEGER
                        WHERE {self.__table__}.sector_gics = %s
                        GROUP BY year, quarter, {self.__table__}.id, {self.__table__}.sub_industry_gics
                        ORDER BY year DESC, quarter DESC;
                    """
        return sql_str

    @classmethod
    def store_records(self, records):    
        avg_financial_by_sub_industries_dict = {} 
        for record in records:
            sub_industry_id, sub_industry_name, financial_item_avg, year_quarter = self.unpack_record(record)
            if sub_industry_name not in avg_financial_by_sub_industries_dict:
                avg_financial_by_sub_industries_dict[sub_industry_name] = {}
            avg_financial_by_sub_industries_dict[sub_industry_name][
                                                                year_quarter] = (sub_industry_id, int(financial_item_avg))
        return avg_financial_by_sub_industries_dict

    @classmethod
    def unpack_record(self, record): # confusing
        sub_industry_id, sub_industry_name, financial_item_avg = record[0], record[1], record[2]
        year, quarter = int(record[3]), int(record[4])
        year_quarter = int(f"{year}0{quarter}") # use integer instead of string?
        return sub_industry_id, sub_industry_name, financial_item_avg, year_quarter

    @classmethod
    def to_historical_financials_json(self, sector_name, financial_item, avg_financial_by_sub_industries_dict):        
        historical_financials_json_dict = {}
        for sub_industry, avg_financials_dict in avg_financial_by_sub_industries_dict.items():
            sub_industry_id, financial_item_avg_recent_quarters = self.unpack_avg_financials_dict(avg_financials_dict)
            historical_financials_json = self.get_historical_financials_json(sub_industry_id, sub_industry, financial_item_avg_recent_quarters) 
            historical_financials_json_dict[sub_industry] = historical_financials_json
        return historical_financials_json_dict
    
    def unpack_avg_financials_dict(avg_financials_dict): # one example of no 'self' argument, and it worked.  Neither a class or instance method?
        sub_industry_id = list(avg_financials_dict.values())[0][0]
        financial_item_avg_recent_quarters = {k:avg_financials_dict[k][1] 
                                                        for k in sorted(avg_financials_dict.keys())} 
        return sub_industry_id, financial_item_avg_recent_quarters

    @classmethod
    def get_historical_financials_json(self, sub_industry_id, sub_industry, financial_item_avg_recent_quarters):
        sub_industry_dict = dict(zip(self.columns,[sub_industry_id, sub_industry, self.sector_name]))
        sub_industry_obj = models.SubIndustry(**sub_industry_dict)
        historical_financials_json = sub_industry_obj.__dict__
        financial_item_key = f'Avg_quarterly_{self.financial_item}'
        historical_financials_json[financial_item_key] = financial_item_avg_recent_quarters
        return historical_financials_json, financial_item_key