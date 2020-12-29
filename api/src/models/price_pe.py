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

    def to_json(self, cursor):
        price_pe_json = self.__dict__
        latest_quarterly_report = self.latest_quarterly_report(cursor)
        if latest_quarterly_report:
            latest_eps_dict = {'earnings_per_share':
                            latest_quarterly_report.earnings_per_share}
            price_pe_json['price_earnings_ratio'] = latest_eps_dict
        return price_pe_json

    def pe_ratio(self, ):
        pass
