"""Industry sector models and related functionality."""
from etl.load.db import connection as db
from etl.transform import models
from psycopg2 import sql
from etl.load.db.query_sector_quarterly_financials import MixinSectorQuarterlyFinancials
from etl.load.db.query_sector_price_pe import MixinSectorPricePE
from etl.load.db.query_sub_sector_price_pe import MixinSubSectorPricePE
from etl.load.db.query_sub_sector_quarterly_financials import Mixin as MixinSubSectorQuarterlyFinancials
from etl.load.db.sql_query_strings import extract_single_financial_indicator, companies_within_sub_sector_str

class SubIndustry(MixinSectorPricePE, MixinSectorQuarterlyFinancials, 
                  MixinSubSectorPricePE, MixinSubSectorQuarterlyFinancials):
    """Represents an industry sub-sector with aggregation capabilities."""

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
    def find_sector_avg_price_pe(self, financial_indicator, cursor):
        all_sectors_price_pe_json = self.to_sector_avg_quarterly_price_pe_json(cursor)
        single_financial_indicator_json = extract_single_financial_indicator(financial_indicator, all_sectors_price_pe_json)
        return single_financial_indicator_json

    @classmethod
    def to_sector_avg_quarterly_price_pe_json(self, cursor):
        sector_names = MixinSectorPricePE.get_all_sector_names(self, cursor)
        sector_avg_price_pe_history_dict = {}
        for sector_name in sector_names:
            sector_avg_price_pe_history_dict[sector_name] = (MixinSectorPricePE.
                                                                    to_avg_quarterly_price_pe_json_by_sector(self, sector_name, cursor))
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
            sector_avg_quarterly_financials_dict[sector_name] = (MixinSectorQuarterlyFinancials.
                                                                        to_avg_quarterly_financials_json_by_sector(self, sector_name, cursor))
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
        sub_industries_quarterly_financials_json = self.to_sub_industry_avg_quarterly_financials_json(sector_name, financial_indicator, cursor)
        single_financial_indicator_json = extract_single_financial_indicator(financial_indicator, sub_industries_quarterly_financials_json)
        return single_financial_indicator_json

    @classmethod
    def to_sub_industry_avg_quarterly_financials_json(self, sector_name, financial_indicator, cursor):
        sub_industry_names = MixinSubSectorPricePE.get_sub_sector_names_of_sector(self, sector_name, cursor)
        avg_quarterly_financials_dict = {}
        for sub_industry_name in sub_industry_names:
            avg_quarterly_financials_dict[sub_industry_name] = (MixinSubSectorQuarterlyFinancials.
                                                                        to_sub_industry_avg_quarterly_financials_json(self, sub_industry_name, cursor))
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
            avg_quarterly_price_pe_dict[sub_industry_name] = (MixinSubSectorPricePE.
                                                                        to_sub_sector_avg_quarterly_price_pe_json(self, sub_industry_name, cursor))
        return avg_quarterly_price_pe_dict

class Sector:
    """Class representing an industry sector."""
    __table__ = 'sectors'
    columns = ['id', 'name']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise ValueError(f"{key} not in {self.columns}")
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_id(cls, sector_id, cursor):
        """Find a sector by ID."""
        sql_str = f"""SELECT * FROM {cls.__table__} 
                      WHERE id = %s;"""
        cursor.execute(sql_str, (sector_id,))
        record = cursor.fetchone()
        if record:
            return cls(**record)
        return None

    @classmethod
    def find_all(cls, cursor):
        """Find all sectors."""
        sql_str = f"""SELECT * FROM {cls.__table__};"""
        cursor.execute(sql_str)
        records = cursor.fetchall()
        return db.build_from_records(cls, records)
