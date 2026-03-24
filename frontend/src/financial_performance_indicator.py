import streamlit as st
from datetime import date


def get_recent_8_quarters() -> list[tuple[int, int]]:
    """Return the 8 most recently completed calendar quarters as (year, quarter), oldest first."""
    today = date.today()
    year, quarter = today.year, (today.month - 1) // 3  # last completed quarter
    if quarter == 0:
        year, quarter = year - 1, 4
    quarters = []
    for _ in range(8):
        quarters.append((year, quarter))
        quarter -= 1
        if quarter == 0:
            year, quarter = year - 1, 4
    return list(reversed(quarters))


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
        
        # Mapping for specific custom naming, otherwise use capitalize
        custom_mapping = {
            'price_earnings_ratio': 'Price-to-Earnings (P/E) Ratio'
        }
        
        indicators_in_frontend_format = [
            custom_mapping.get(indicator, ' '.join([word.capitalize() for word in indicator.split('_')]))
            for indicator in indicators_in_backend_format
        ]
        return indicators_in_frontend_format

    def select_from_financial_indicators_menu(self, financial_indicator, streamlit_key):
        self.indicators_in_backend_format.remove(financial_indicator)
        self.indicators_in_backend_format = [financial_indicator] + self.indicators_in_backend_format
        indicators_in_frontend_format = self.get_indicators_in_frontend_format(
                                                        self.indicators_in_backend_format)
        selected_financial_indicator = st.selectbox('Financial Indicator', indicators_in_frontend_format, index=0, key=streamlit_key, label_visibility='collapsed')
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
        financial_item_unit_mapping = {
            'revenue':              'USD (billions)',
            'net_income':           'USD (millions)',
            'earnings_per_share':   'USD',
            'closing_price':        'USD',
            'profit_margin':        'Percentage',
            'price_earnings_ratio': 'P/E Ratio (x)',
        }
        return financial_item_unit_mapping.get(financial_item, 'USD')
