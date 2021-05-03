
def unpack_year_quarter(year_quarter:int):
    year = str(year_quarter)[:4]
    quarter = str(year_quarter[-1])
    return f'{year}-{quarter} Quarter'


def get_financial_item_unit(financial_item):
    usd_financial_items = ['revenue', 'net_income', 'earnings_per_share', 'closing_price']
    financial_item_unit_dict = {usd_item: 'USD' for usd_item in usd_financial_items}
    financial_item_unit_dict['profit_margin'] = 'percentage'
    financial_item_unit_dict['price_earnings_ratio'] = ''
    return financial_item_unit_dict[financial_item]