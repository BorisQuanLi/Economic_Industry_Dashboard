from etl.load.db.sql_query_strings import companies_within_sub_sector_str, company_quarterly_financials_query_str
from etl.transform.models.analytics.aggregation_by_quarter import QuarterlyFinancials

class MixinCompanyFinancials:
    """mixin with class Company"""

    def to_quarterly_financials_json(self, company_name, cursor):
        sql_str = company_quarterly_financials_query_str(self)
        cursor.execute(sql_str, (company_name,))
        objs_list = [self.create_quarterly_financials_objs(self, record[1:]) for record in cursor.fetchall()]
        return objs_list

    def create_quarterly_financials_objs(self, record):
        attr_record_dict = dict(zip(QuarterlyReportResult.attributes, record))
        obj = QuarterlyReportResult(**attr_record_dict)
        return obj.__dict__
