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

    @classmethod
    def find_by_company_id(self, company_id, cursor):
        sql_str = f"""SELECT * FROM {self.__table__}
                        WHERE company_id = %s;"""
        cursor.execute(sql_str, (company_id,))
        records = cursor.fetchall()
        return db.build_from_records(models.SubIndustry, records)