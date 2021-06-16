from api.src.models.quarterly_aggregation_models.aggregation_by_quarter import QuarterlyReportResult
from api.src.models.queries.sql_query_strings import per_sector_avg_quarterly_financials_query_str 

class Mixin:
    def to_avg_quarterly_financials_json_by_sector(self, sector_name, cursor):
        sql_str = per_sector_avg_quarterly_financials_query_str(self)
        cursor.execute(sql_str, (sector_name,))
        sector_avg_quarterly_financials_records = [record[1:] for record in cursor.fetchall()]
        avg_quarterly_financial_objs = [self.build_avg_quarterly_financials_obj(self, record, cursor)
                                                                        for record in sector_avg_quarterly_financials_records]
        return avg_quarterly_financial_objs

    def build_avg_quarterly_financials_obj(self, sector_avg_financial_quarterly_record, cursor):
        attrs = ['year', 'quarter', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin']
        quarterly_obj = QuarterlyReportResult(**dict(zip(attrs, sector_avg_financial_quarterly_record)))
        return quarterly_obj.__dict__

 