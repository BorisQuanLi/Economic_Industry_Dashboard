

class Price:
    __tables__ = 'prices'
    columns = ['id', 'date', 'company_id', 'closing_price']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f'{key} not in {self.columns}'
            for k, v in kwargs.items():
                setattr(self, k, v)