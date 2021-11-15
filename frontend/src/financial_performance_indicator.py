import streamlit as st

class FinancialPerformanceIndicator:

    def __init__(self):
        self.indicators_in_backend_format = [
                'revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'closing_price', 'price_earnings_ratio'
                ]

    def frontend_backend_string_format_mapping(self, financial_item, direction = 'frontend-to-backend'):
        """
        Transform the string format of a variable in the backend codebase, storing a financial performance indicator with
        all lowercase letters and, where needed, underscores between words, to capitalized letters, with white spaces 
        between words.
        """   
        indicators_in_frontend_format = self.get_indicators_in_frontend_format()
        backend_to_frontend_str_format_mapping = dict(zip(self.indicators_in_backend_format, 
                                                            indicators_in_frontend_format))
        frontend_to_backend_str_format_mapping = dict(zip(indicators_in_frontend_format, 
                                                            self.indicators_in_backend_format))
        if direction == 'frontend-to-backend': return frontend_to_backend_str_format_mapping[financial_item]
        else: return backend_to_frontend_str_format_mapping[financial_item]

    def get_indicators_in_frontend_format(self, indicators_in_backend_format=None):
        if not indicators_in_backend_format:
            indicators_in_backend_format = self.indicators_in_backend_format
        indicators_in_frontend_format = [' '.join([word.capitalize() for word in indicator.split('_')]) 
                                                                        for indicator in indicators_in_backend_format]
        return indicators_in_frontend_format

    def select_from_financial_indicators_menu(self, financial_indicator, streamlit_key):
        self.indicators_in_backend_format.remove(financial_indicator)
        self.indicators_in_backend_format = [financial_indicator] + self.indicators_in_backend_format
        indicators_in_frontend_format = self.get_indicators_in_frontend_format(
                                                        self.indicators_in_backend_format)
        selected_financial_indicator = st.selectbox('', indicators_in_frontend_format, index=0, key= streamlit_key)
        selected_financial_indicator = self.frontend_backend_string_format_mapping(selected_financial_indicator)
        return selected_financial_indicator

    def extract_year_quarter(self, quarterly_dict:dict):
        """
        transform the year, month values of the argument (a dictionary), 
        return them in the string format "quarter-number yyyy" 
        """
        year = str(int(quarterly_dict['year']))
        quarter_month_mapping = dict(zip(range(1,5), 
                                            ['March', 'June', 'September', 'December']))
        quarter_ending_month = quarter_month_mapping[int(quarterly_dict['quarter'])]
        return f'{quarter_ending_month} {year}'

    def get_financial_item_unit(self, financial_item):
        usd_financial_items = ['revenue', 'net_income', 'earnings_per_share', 'closing_price']
        financial_item_unit_mapping = {usd_item: 'USD' for usd_item in usd_financial_items}
        financial_item_unit_mapping['profit_margin'] = 'percentage'
        financial_item_unit_mapping['price_earnings_ratio'] = ''
        return financial_item_unit_mapping[financial_item]
