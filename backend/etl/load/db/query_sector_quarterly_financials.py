"""Queries for sector quarterly financial data."""
from etl.transform.models.analytics.aggregation_by_quarter import QuarterlyReportResult
from etl.load.db.sql_query_strings import select_avg_financials_quarterly_by_sector

class MixinSectorQuarterlyFinancials:
    """Mixin that provides methods for querying sector quarterly financial data."""
    def to_avg_quarterly_financials_json_by_sector(self, sector_name, cursor):
        sql_str = select_avg_financials_quarterly_by_sector(self)
        cursor.execute(sql_str, (sector_name,))
        sector_avg_quarterly_financials_records = [record[1:] for record in cursor.fetchall()]
        avg_quarterly_financial_objs = [self.build_avg_quarterly_financials_obj(self, record, cursor)
                                                                        for record in sector_avg_quarterly_financials_records]
        return avg_quarterly_financial_objs

    def build_avg_quarterly_financials_obj(self, sector_avg_financial_quarterly_record, cursor):
        attrs = ['year', 'quarter', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin']
        quarterly_obj = QuarterlyReportResult(**dict(zip(attrs, sector_avg_financial_quarterly_record)))
        return quarterly_obj.__dict__

