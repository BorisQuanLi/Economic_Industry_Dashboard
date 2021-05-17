from api.src.models.aggregation_averaging.aggregation_by_quarter import QuarterlyPricePE
from api.src.models.queries.sql_query_strings import (query_all_sector_records, 
                                                      sector_avg_price_pe_history_query_str)

"""
The "definitive version" in:
http://www.qtrac.eu/pyclassmulti.html
"""

class Mixin:
    def get_all_sector_names(self, cursor):
        sql_str = query_all_sector_records(self)
        cursor.execute(sql_str)
        sector_names = [sector_record[0] for sector_record in cursor.fetchall()]
        return sector_names

    def to_avg_quarterly_price_pe_json_by_sector(self, sector_name, cursor):
        sql_str = sector_avg_price_pe_history_query_str(self)
        cursor.execute(sql_str, (sector_name,)) 
        avg_quarterly_price_pe_objs = [self.build_avg_quarterly_price_pe_obj(self, record, cursor)
                                                                        for record in cursor.fetchall()]
        return avg_quarterly_price_pe_objs

    def build_avg_quarterly_price_pe_obj(self, sector_avg_price_pe_quarterly_record, cursor):
        quarterly_obj = QuarterlyPricePE(**dict(zip(QuarterlyPricePE.attributes, 
                                                    sector_avg_price_pe_quarterly_record)))
        return quarterly_obj.__dict__
