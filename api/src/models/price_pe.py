from api.src.db import db
from api.src import models

class PricePE:
    __table__ = 'prices_pe' 
    columns = ['id', 'date', 'company_id', 'closing_price', 'price_earnings_ratio']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f"{key} not in {self.columns}"
        for k, v in kwargs.items():
            setattr(self, k, v)

    def latest_quarterly_report(self, cursor):
        sql_query = f"""SELECT * FROM quarterly_reports
                    WHERE company_id = %s
                    ORDER BY date DESC 
                    LIMIT 1;
                    """
        cursor.execute(sql_query, (self.company_id,))
        record = cursor.fetchone()
        return db.build_from_record(models.QuarterlyReport, record)

    def to_latest_pe_json(self, cursor):
        latest_price_pe_json = self.__dict__
        latest_quarterly_report = self.latest_quarterly_report(cursor)
        if latest_quarterly_report:
            pe_ratio = round(self.closing_price / latest_quarterly_report.earnings_per_share, 2)
            latest_price_pe_json['price_earnings_ratio'] = pe_ratio
        return latest_price_pe_json

    def quarterly_reports(self, cursor):
        sql_query = f"""SELECT * FROM quarterly_reports
                        WHERE company_id = %s
                        ORDER BY date DESC;
                    """
        cursor.execute(sql_query, (self.company_id,))
        records = cursor.fetchall()
        return db.build_from_records(QuarterlyReport, records)

    def to_pe_json_list(self, cursor):
        quarterly_reports = self.quarterly_reports(cursor)
        pe_json_list = []
        for quarter in quarterly_reports:
            date = quarter.date
            # quarter.date + 20 days? -> finnhub.io price history
            sql_query = f"""SELECT price FROM {self.__table__}
                            WHERE date = %s;
                        """
            cursor.execute(sql_query, (date,))
            price = cursor.fetchone()
            to_pe_json = self.__dict__
            to_pe_json['price'] = price
            to_pe_json['price_earnings_ratio'] = (
                                        price / quarter.earnings_per_share)
            quarter.earnings_per_share
        return pe_json_list