"""Queries for sub-sector quarterly financial data."""
from etl.transform.models.aggregate_analytics.aggregation_by_quarter import QuarterlyReportResult
from etl.load.db.sql_query_strings import sub_industry_avg_quarterly_financial_query_str

class Mixin:
    """Mixin that provides methods for querying sub-sector quarterly financial data."""
    def to_sub_industry_avg_quarterly_financials_json(self, sub_industry_name, cursor):
        sql_str = sub_industry_avg_quarterly_financial_query_str(self)
        cursor.execute(sql_str, (sub_industry_name,))
        objs_list = [self.create_avg_quarterly_financialsobjs(self, record[1:]) 
                                                            for record in cursor.fetchall()]
        return objs_list

    def create_avg_quarterly_financialsobjs(self, record):
        attr_record_dict = dict(zip(QuarterlyReportResult.attributes, 
                                    record))
        obj = QuarterlyReportResult(**attr_record_dict)
        return obj.__dict__
