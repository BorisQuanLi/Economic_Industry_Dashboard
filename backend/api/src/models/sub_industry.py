from api.src.db import db
import api.src.models as models
from psycopg2 import sql
from api.src.models.queries.query_sector_quarterly_financials import MixinSectorQuarterlyFinancials
from api.src.models.queries.query_sector_price_pe import MixinSectorPricePE
from api.src.models.queries.query_sub_sector_price_pe import MixinSubSectorPricePE
from api.src.models.queries.query_sub_sector_quarterly_financials import MixinSubSectorQuarterlyFinancials
from api.src.models.queries.sql_query_strings import extract_single_financial_indicator, companies_within_sub_sector_str, find_sub_industry_by_name_str

class SubIndustry(MixinSectorPricePE,  # create new class called Sector and sub-Sector, or Quarterly Financials and Prices PE
                  MixinSectorQuarterlyFinancials, # do the above in models/aggregation_by_quarter.py?
                  MixinSubSectorPricePE,
                  MixinSubSectorQuarterlyFinancials):

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
        """ to be called by run_adapters.py """
        sql_query = """SELECT * FROM sub_industries 
                        WHERE sub_industry_gics = %s;
                    """
        cursor.execute(sql_query, (sub_industry_name,))
        record = cursor.fetchone()
        return db.build_from_record(self, record)

    @classmethod
    def find_by_name(self, name, cursor):
        sql_str = find_sub_industry_by_name_str()
        cursor.execute(sql_str, (name,))
        record = cursor.fetchone()
        return SubIndustry(*record)

    def get_financial_indicator_by_quarter(self, financial_indicator, date):
        return 1000.0

    @classmethod
    def find_sector_avg_price_pe(self, financial_indicator, cursor):
        all_sectors_price_pe_json = self.to_sector_avg_quarterly_price_pe_json(cursor)
        single_financial_indicator_json = extract_single_financial_indicator(financial_indicator, all_sectors_price_pe_json)
        return single_financial_indicator_json

    @classmethod
    def to_sector_avg_quarterly_price_pe_json(self, cursor):
        sector_names = MixinSectorPricePE.get_all_sector_names(self, cursor)
        sector_avg_price_pe_history_dict = {}
        for sector_name in sector_names:
            sector_avg_price_pe_history_dict[sector_name] = self.to_avg_quarterly_price_pe_json_by_sector(sector_name, cursor)
        return sector_avg_price_pe_history_dict

    @classmethod
    def find_avg_quarterly_financials_by_sector(self, financial_indicator, cursor):
        all_sectors_quarterly_financials_json = self.to_avg_quarterly_financials_by_sector_json(cursor)
        single_financial_indicator_json = extract_single_financial_indicator(financial_indicator, all_sectors_quarterly_financials_json)        
        return single_financial_indicator_json

    @classmethod
    def to_avg_quarterly_financials_by_sector_json(self, cursor):
        sector_names = MixinSectorPricePE.get_all_sector_names(self, cursor)
        sector_avg_quarterly_financials_dict = {}
        for sector_name in sector_names:
            sector_avg_quarterly_financials_dict[sector_name] = self.to_avg_quarterly_financials_json_by_sector(sector_name, cursor)
        return sector_avg_quarterly_financials_dict
    
    ### find_sub_industry_avg_quarterly_financials
    @classmethod
    def find_avg_quarterly_financials_by_sub_industry(self, sector_name:str, financial_indicator:str, cursor):
        """
        Within each chosen sector, calculate each sub_industry's average value of a chosen
        financial-statement item (revenue, net_profit, etc.) over the most recent 8 quarters.

        Returns a list of dictionaries with the key being a list of attributes, incl. [sector_name,
        financial_indicator name, year, quarter], and their corresponding values stored in a list as 
        the dictionary value.
        """
        sub_industries_quarterly_financials_json = self.to_all_sub_industries_avg_quarterly_financials_json(sector_name, financial_indicator, cursor)
        single_financial_indicator_json = extract_single_financial_indicator(financial_indicator, sub_industries_quarterly_financials_json)
        return single_financial_indicator_json

    @classmethod
    def to_all_sub_industries_avg_quarterly_financials_json(self, sector_name, financial_indicator, cursor):
        sub_industry_names = MixinSubSectorPricePE.get_sub_sector_names_of_sector(self, sector_name, cursor)
        avg_quarterly_financials_dict = {}
        for sub_industry_name in sub_industry_names:
            avg_quarterly_financials_dict[sub_industry_name] = self.to_sub_industry_avg_quarterly_financials_json(sub_industry_name, cursor)
        return avg_quarterly_financials_dict

    @classmethod
    def find_sub_industry_avg_quarterly_price_pe(self, sector_name:str, financial_indicator:str, cursor):
        sub_industries_quarterly_price_pe_json = self.to_sub_industry_avg_quarterly_price_pe_json(sector_name, financial_indicator, cursor)
        single_financial_indicator_json = extract_single_financial_indicator(financial_indicator, sub_industries_quarterly_price_pe_json)
        return single_financial_indicator_json
    
    @classmethod
    def to_sub_industry_avg_quarterly_price_pe_json(self, sector_name, financial_indicator, cursor):
        sub_industry_names = MixinSubSectorPricePE.get_sub_sector_names_of_sector(self, sector_name, cursor)
        avg_quarterly_price_pe_dict = {}
        for sub_industry_name in sub_industry_names:
            avg_quarterly_price_pe_dict[sub_industry_name] = self.to_sub_sector_avg_quarterly_price_pe_json(sub_industry_name, cursor)
        return avg_quarterly_price_pe_dict
