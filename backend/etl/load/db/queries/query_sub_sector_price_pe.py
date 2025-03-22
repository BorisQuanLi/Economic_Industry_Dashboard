"""Queries for sub-sector price and PE ratio data."""
from etl.transform.models.aggregate_analytics.aggregation_by_quarter import QuarterlyPricePE
from etl.load.db.sql_query_strings import (sub_sector_names_in_sector_query_str,
                                           sub_sector_avg_quarterly_price_pe_history_query_str)

class MixinSubSectorPricePE:
    """Mixin that provides methods for querying sub-sector price and PE ratio data."""
    def get_sub_sector_names_of_sector(self, sector_name, cursor):
        sql_str = sub_sector_names_in_sector_query_str()
        cursor.execute(sql_str, (sector_name,))
        sub_sector_names = [sub_sector_record[0] for sub_sector_record in cursor.fetchall()]
        return sub_sector_names

    def to_sub_sector_avg_quarterly_price_pe_json(self, sub_industry_name, cursor):
        sql_str = sub_sector_avg_price_pe_history_query_str(self)
        cursor.execute(sql_str, (sub_industry_name,))
        objs_list = [self.create_objs(self, record[1:]) for record in cursor.fetchall()]
        return objs_list

    def create_objs(self, record):
        attr_record_dict = dict(zip(QuarterlyPricePE().attributes, 
                                    record))
        obj = QuarterlyPricePE(**attr_record_dict)
        return obj.__dict__