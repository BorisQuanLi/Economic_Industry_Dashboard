from api.src.models.quarterly_aggregation_models.aggregation_by_quarter import QuarterlyPricePE
from api.src.models.queries.sql_query_strings import (sub_industry_names_in_sector_query_str, 
                                                      sub_industry_avg_price_pe_history_query_str)

class Mixin:
    def get_sub_industry_names_of_sector(self, sector_name, cursor):
        sql_str = sub_industry_names_in_sector_query_str(self)
        cursor.execute(sql_str, (sector_name,))
        sector_names = [sector_record[0] for sector_record in cursor.fetchall()]
        return sector_names

    def to_sub_industry_avg_quarterly_price_pe_json(self, sub_industry_name, cursor):
        sql_str = sub_industry_avg_price_pe_history_query_str(self)
        cursor.execute(sql_str, (sub_industry_name,))
        objs_list = [self.create_objs(self, record[1:]) for record in cursor.fetchall()]
        return objs_list

    def create_objs(self, record):
        attr_record_dict = dict(zip(QuarterlyPricePE().attributes, 
                                    record))
        obj = QuarterlyPricePE(**attr_record_dict)
        return obj.__dict__