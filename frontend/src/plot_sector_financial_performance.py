import streamlit as st
import requests
import plotly.graph_objects as go
from frontend_utilities import (assemble_year_quarter, get_financial_item_unit, 
                                underscored_to_spaced_words_dict, underscored_to_spaced_words_dict, 
                                frontend_backend_string_format_conversion, get_indicators_in_frontend_format)

AGGREGATION_BY_SECTOR_URL = "http://127.0.0.1:5000/sectors"

def plot_sector_level_performance():
    st.header('Historical financial performance by economic sectors.')
    st.header(' ')
    done_statement = 'Done. Continue to the sub-Sector level.'
    indicators_in_backend_format = ['closing_price', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'price_earnings_ratio'] + [done_statement]
    indicators_in_frontend_format = get_indicators_in_frontend_format(indicators_in_backend_format)
    st.write("Please select a financial performance indicator from this drop-down menu:")
    selected_financial_indicator = st.selectbox('', indicators_in_frontend_format, key= 'sector_level')
    selected_financial_indicator = frontend_backend_string_format_conversion()[selected_financial_indicator]
    plot_selected_financial_indicator(selected_financial_indicator)
    return None

def plot_selected_financial_indicator(financial_indicator):
    fig = go.Figure()
    get_plotly_chart_data(fig, financial_indicator)
    update_layout(fig, financial_indicator)
    st.plotly_chart(fig, use_container_width= True)

def get_plotly_chart_data(fig, financial_indicator):
    try:
        quarterly_financial_history_by_sector = find_sector_avg_financials(financial_indicator)
        for sector, quarterly_financials in quarterly_financial_history_by_sector.items():
            x_axis_time_series, y_axis_financials = get_time_n_financials_axis(sector,
                                                                                quarterly_financials,
                                                                                financial_indicator)
            add_trace(fig, sector, x_axis_time_series, y_axis_financials)
    except Exception as e:
        print(e)
        print(quarterly_financial_history_by_sector)
        breakpoint()

def find_sector_avg_financials(financial_indicator):
    response_dict = requests.get(AGGREGATION_BY_SECTOR_URL, params= {'financial_indicator': financial_indicator})
    return response_dict.json()

def get_time_n_financials_axis(sector, quarterly_financials, financial_indicator):
    x_axis_time_series = [assemble_year_quarter(quarterly_dict) for quarterly_dict in quarterly_financials]
    y_axis_financials = [quarterly_dict[financial_indicator] for quarterly_dict in quarterly_financials]
    return x_axis_time_series, y_axis_financials

def add_trace(fig, sector, x_axis_time_series, y_axis_financials):
    fig.add_trace(go.Scatter(x = x_axis_time_series,
                            y = y_axis_financials,
                            mode = 'lines',
                            name = sector))

def update_layout(fig, financial_indicator):
    return fig.update_layout(
                                title= f"{underscored_to_spaced_words_dict(financial_indicator)} (Average)",
                                yaxis_title= get_financial_item_unit(financial_indicator),
                                legend_title="Economic sectors",
                                font=dict(
                                            family="Courier New, monospace",
                                            size=18,
                                            color="RebeccaPurple"
                                        )
                            )

