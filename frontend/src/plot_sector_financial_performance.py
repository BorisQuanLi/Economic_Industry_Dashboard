import streamlit as st
import requests
import plotly.graph_objects as go
from financial_performance_indicator import FinancialPerformanceIndicator

AGGREGATION_BY_SECTOR_URL = "http://fastapi_backend:8000/api/v1/sectors"

def plot_sector_level_performance():
    st.header('Historical financial performance by economic sectors.')
    st.header(' ')
    financial_performance_indicators = FinancialPerformanceIndicator()
    indicators_in_frontend_format = financial_performance_indicators.get_indicators_in_frontend_format()
    st.write("Please select a financial performance indicator from this drop-down menu:")
    selected_financial_indicator = st.selectbox('', indicators_in_frontend_format, key= 'sector_level')
    # default st.selectbox() selection is 'closing_price', the first element of the indicators_in_frontend_format list 
    selected_financial_indicator_backend_format = (financial_performance_indicators
                                                        .frontend_backend_string_format_mapping(
                                                            selected_financial_indicator)
                                                    )
    plot_selected_financial_indicator(selected_financial_indicator_backend_format, financial_performance_indicators)
    return selected_financial_indicator_backend_format

def plot_selected_financial_indicator(financial_indicator, financial_performance_indicators):
    fig = go.Figure()
    get_plotly_chart_data(fig, financial_indicator, financial_performance_indicators)
    update_layout(fig, financial_indicator, financial_performance_indicators)
    st.plotly_chart(fig, use_container_width= True)

def get_plotly_chart_data(fig, financial_indicator, financial_performance_indicators):
    quarterly_financial_history_by_sector = None
    try:
        quarterly_financial_history_by_sector = find_sector_avg_financials(financial_indicator)
        for sector, quarterly_financials in quarterly_financial_history_by_sector.items():
            x_axis_time_series, y_axis_financials = get_time_n_financials_axis(sector,
                                                                                quarterly_financials,
                                                                                financial_indicator,
                                                                                financial_performance_indicators)
            add_trace(fig, sector, x_axis_time_series, y_axis_financials)
    except Exception as e:
        print(e)
        print(quarterly_financial_history_by_sector)
        breakpoint()

def find_sector_avg_financials(financial_indicator):
    response_dict = requests.get(AGGREGATION_BY_SECTOR_URL, params= {'financial_indicator': financial_indicator})
    return response_dict.json()

def get_time_n_financials_axis(sector, quarterly_financials, financial_indicator, financial_performance_indicators):
    x_axis_time_series = [financial_performance_indicators.extract_year_quarter(quarterly_dict) 
                                                        for quarterly_dict in quarterly_financials]
    y_axis_financials = [quarterly_dict[financial_indicator] for quarterly_dict in quarterly_financials]
    return x_axis_time_series, y_axis_financials

def add_trace(fig, sector, x_axis_time_series, y_axis_financials):
    fig.add_trace(go.Scatter(x = x_axis_time_series,
                            y = y_axis_financials,
                            mode = 'lines',
                            name = sector))

def update_layout(fig, financial_indicator, financial_performance_indicators):
    return fig.update_layout(
                title= f"Average {financial_performance_indicators.frontend_backend_string_format_mapping(financial_indicator, 'backend-to-frontend')}",
                yaxis_title= financial_performance_indicators.get_financial_item_unit(financial_indicator),
                legend_title="Economic sectors",
                font=dict(
                            family="Courier New, monospace",
                            size=18,
                            color="RebeccaPurple"
                        )
                            )

