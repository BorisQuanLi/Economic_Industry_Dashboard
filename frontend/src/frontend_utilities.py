import streamlit as st

def welcome_message():
    st.title("Welcome to the Economic Analysis api, through the prism of the S&P 500 stocks performance.")
    st.title(" ")
    st.write("                           by Boris Li, 2021")


def frontend_backend_string_format_conversion(direction = 'frontend-to-backend-translation'):
    indicators_in_backend_format = ['revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'closing_price', 'price_earnings_ratio']
    indicators_in_frontend_format = get_indicators_in_frontend_format(indicators_in_backend_format)
    backend_to_frontend_format_dict = dict(zip(indicators_in_backend_format, indicators_in_frontend_format))
    frontend_to_backend_format_dict = dict((zip(indicators_in_frontend_format, indicators_in_backend_format)))
    if direction == 'frontend-to-backend-translation': return frontend_to_backend_format_dict
    else: return backend_to_frontend_format_dict

def get_indicators_in_frontend_format(indicators_in_backend_format):
    indicators_in_frontend_format = [' '.join([word.capitalize() for word in term.split('_')]) 
                                                                for term in indicators_in_backend_format]
    return indicators_in_frontend_format

def assemble_year_quarter(quarterly_dict:dict()):
    year = str(int(quarterly_dict['year']))
    quarter_ending_month_dict = dict(zip(range(1,5), 
                                        ['March', 'June', 'September', 'December']))
    quarter_ending_month = quarter_ending_month_dict[int(quarterly_dict['quarter'])]

    return f'{quarter_ending_month} {year}'

def get_financial_item_unit(financial_item):
    usd_financial_items = ['revenue', 'net_income', 'earnings_per_share', 'closing_price']
    financial_item_unit_dict = {usd_item: 'USD' for usd_item in usd_financial_items}
    financial_item_unit_dict['profit_margin'] = 'percentage'
    financial_item_unit_dict['price_earnings_ratio'] = ''
    return financial_item_unit_dict[financial_item]

def underscored_to_spaced_words_dict(underscored_words_financial_item, 
                                     underscored_words_financial_items 
                                        = ['revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'closing_price', 'price_earnings_ratio']):
    spaced_words_financial_items = underscored_to_spaced(
                                                    underscored_words_financial_items)
    conversion_dict = dict(zip(underscored_words_financial_items,
                                spaced_words_financial_items))
    return conversion_dict[underscored_words_financial_item]

def spaced_to_underscored_words_dict(spaced_words_financial_item,
                                     spaced_words_financial_items
                                        = ['Revenue', 'Net Income', 'Earnings Per Share', 'Profit Margin', 'Closing Price', 'Price Earnings Ratio']):
    underscored_words_financial_items = spaced_to_underscored(spaced_words_financial_items)
    conversion_dict = dict(zip(spaced_words_financial_items,
                                underscored_words_financial_items))
    return conversion_dict[spaced_words_financial_item]

def underscored_to_spaced(underscored_words_financial_items:list):
    transformed_financial_items_list = []
    for underscored_words in underscored_words_financial_items:
        if '_' not in underscored_words:
            transformed_financial_items_list.append(underscored_words.capitalize())
        else:
            spaced_words = ' '.join([word.capitalize() 
                                            for word in underscored_words.split('_')])
            transformed_financial_items_list.append(spaced_words)
    return transformed_financial_items_list      

def spaced_to_underscored(spaced_words_financial_items:list):
    underscored_words_list = []
    for words in spaced_words_financial_items:
        underscored_words = '_'.join(words.lower().split(' '))
        underscored_words_list.append(underscored_words)
    return underscored_words_list
