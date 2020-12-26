

class Price:
    __table__ = 'prices'
    columns = ['id', 'date', 'company_id', 'closing_price']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f'{key} not in {self.columns}'
            for k, v in kwargs.items():
                setattr(self, k, v)

    def find_price_by_date(self, date, company_id, cursor):
        sql_str = f"""SELECT * FROM {self.__table__}
                    WHERE company_id = %s AND date = %s;"""
        cursor.execute(sql_str, (company_id, date))
        record = cursor.fetchone()
        return record
