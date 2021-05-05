import streamlit as st
import requests
import plotly.graph_objects as go
from helpers import (unpack_year_quarter, get_financial_item_unit, provide_financial_indicator_choice_menu,
                    underscored_to_spaced_words_dict, spaced_to_underscored_words_dict)

AGGREGATION_BY_SECTOR_URL = "http://127.0.0.1:5000/sectors"

def plot_sectors_performance(AGGREGATION_BY_SECTOR_URL):
    st.title('Historical financial performance by economic sectors.')
    st.title(' ')
    st.write('Please choose a financial performance indicator from')
    """
    # st.multiselect()
    financial_items = [underscored_to_spaced_words_dict(item)
                                for item in ['revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'closing_price', 'price_earnings_ratio']]
    financial_items_selected = st.multiselect('Please select a financial-statement item:', financial_items, financial_items)
    financial_items_selected = [spaced_to_underscored_words_dict(item) for item in financial_items_selected]
    """
    
    selected_financial_indicator = provide_financial_indicator_choice_menu()
    if not selected_financial_indicator:
        print(selected_financial_indicator)
        breakpoint()
    breakpoint()
    plot_selected_financial_items(financial_items_selected)

def plot_selected_financial_items(financial_items_selected):
    for financial_item in financial_items_selected:
        fig = go.Figure()
        get_plotly_chart_data(fig, financial_item)
        update_layout(fig, financial_item)
        st.plotly_chart(fig, use_container_width= True)

def get_plotly_chart_data(fig, financial_item):
    quarterly_financial_history_by_sector = find_sector_avg_financials(financial_item)
    for sector, quarterly_financials in quarterly_financial_history_by_sector.items():
        x_axis_time_series, y_axis_financials = get_time_n_financials_axis(sector,
                                                                            quarterly_financials,
                                                                            financial_item)
        add_trace(fig, sector, x_axis_time_series, y_axis_financials)

def find_sector_avg_financials(financial_item):
    response_dict = requests.get(AGGREGATION_BY_SECTOR_URL, params= {'financial_item': financial_item})
    return response_dict.json()

def get_time_n_financials_axis(sector, quarterly_financials, financial_item):
    x_axis_time_series = [unpack_year_quarter(year_quarter) for year_quarter in quarterly_financials.keys()]
    y_axis_financials = [(financials[f'avg_{financial_item}']) for financials in quarterly_financials.values()]
    return x_axis_time_series, y_axis_financials

def add_trace(fig, sector, x_axis_time_series, y_axis_financials):
    fig.add_trace(go.Scatter(x = x_axis_time_series,
                            y = y_axis_financials,
                            mode = 'lines',
                            name = sector))

def update_layout(fig, financial_item):
    return fig.update_layout(
                                title= f"{underscored_to_spaced_words_dict(financial_item)} (Average)",
                                yaxis_title= get_financial_item_unit(financial_item),
                                legend_title="Economic sectors",
                                font=dict(
                                            family="Courier New, monospace",
                                            size=18,
                                            color="RebeccaPurple"
                                        )
                            )

