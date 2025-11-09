from api.src.models.quarterly_aggregation_models.aggregation_by_quarter import QuarterlyReportResult
from api.src.models.queries.sql_query_strings import sub_industry_avg_quarterly_financial_query_str

class MixinSubSectorQuarterlyFinancials:
    @classmethod
    def to_sub_industry_avg_quarterly_financials_json(self, sub_industry_name, cursor):
        sql_str = sub_industry_avg_quarterly_financial_query_str(self)
        cursor.execute(sql_str, (sub_industry_name,))
        objs_list = [self.create_avg_quarterly_financialsobjs(record[1:]) 
                                                            for record in cursor.fetchall()]
        return objs_list

    @classmethod
    def create_avg_quarterly_financialsobjs(self, record):
        attr_record_dict = dict(zip(QuarterlyReportResult.attributes, 
                                    record))
        obj = QuarterlyReportResult(**attr_record_dict)
        return obj.__dict__
