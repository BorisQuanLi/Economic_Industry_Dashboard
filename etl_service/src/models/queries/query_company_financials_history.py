from api.src.models.queries.sql_query_strings import companies_within_sub_sector_str, company_quarterly_financials_query_str
from api.src.models.quarterly_aggregation_models.aggregation_by_quarter import QuarterlyReportResult
class MixinCompanyFinancials:
    """mixin with class Company"""

    def to_quarterly_financials_json(self, company_name, cursor):
        sql_str = company_quarterly_financials_query_str(self)
        cursor.execute(sql_str, (company_name,))
        objs_list = [self.create_quarterly_financials_objs(record[1:]) for record in cursor.fetchall()]
        return objs_list

    def create_quarterly_financials_objs(self, record):
        attr_record_dict = dict(zip(QuarterlyReportResult.attributes, record))
        obj = QuarterlyReportResult(**attr_record_dict)
        return obj.__dict__
