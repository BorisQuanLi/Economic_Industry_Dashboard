import streamlit as st
import requests
import plotly.graph_objects as go
import math
from chart_layout import apply_standard_chart_layout
from financial_performance_indicator import FinancialPerformanceIndicator

AGGREGATION_BY_SECTOR_URL = "http://fastapi_backend:8000/api/v1/sectors"

def plot_sector_level_performance():
    st.header('Historical financial performance by economic sectors.')
    st.header(' ')
    financial_performance_indicators = FinancialPerformanceIndicator()
    indicators_in_frontend_format = financial_performance_indicators.get_indicators_in_frontend_format()
    st.write("Please select a financial performance indicator from this drop-down menu:")
    selected_financial_indicator = st.selectbox('Financial Indicator', indicators_in_frontend_format, key= 'sector_level', label_visibility='collapsed')
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
    st.plotly_chart(fig, use_container_width=True, key=f"sector_chart_{financial_indicator}", theme=None)

def get_plotly_chart_data(fig, financial_indicator, financial_performance_indicators):
    quarterly_financial_history_by_sector = None
    try:
        quarterly_financial_history_by_sector = find_sector_avg_financials(financial_indicator)
        for sector, quarterly_financials in quarterly_financial_history_by_sector.items():
            if not sector or not quarterly_financials:
                continue
            x_axis_time_series, y_axis_financials = get_time_n_financials_axis(sector,
                                                                                quarterly_financials,
                                                                                financial_indicator,
                                                                                financial_performance_indicators)
            if x_axis_time_series and y_axis_financials:
                add_trace(fig, sector, x_axis_time_series, y_axis_financials)
    except Exception as e:
        print(f"Error in get_plotly_chart_data: {e}")
        print(f"Data received: {quarterly_financial_history_by_sector}")
        st.error(f"Unable to load chart data: {e}")

def find_sector_avg_financials(financial_indicator):
    response_dict = requests.get(AGGREGATION_BY_SECTOR_URL, params= {'financial_indicator': financial_indicator})
    return response_dict.json()

def get_time_n_financials_axis(sector, quarterly_financials, financial_indicator, financial_performance_indicators):
    x_axis_time_series = []
    y_axis_financials = []

    for quarterly_dict in quarterly_financials:
        if not isinstance(quarterly_dict, dict):
            continue
        if financial_indicator not in quarterly_dict:
            continue

        value = quarterly_dict.get(financial_indicator)
        if not isinstance(value, (int, float)) or not math.isfinite(value):
            continue
        
        # Scaling specifically for Net Income (Conversion from Billions to Millions)
        if financial_indicator == 'net_income':
            value = value * 1000

        try:
            date_label = financial_performance_indicators.extract_year_quarter(quarterly_dict)
        except (KeyError, TypeError, ValueError):
            continue

        x_axis_time_series.append(date_label)
        y_axis_financials.append(value)

    return x_axis_time_series, y_axis_financials

def add_trace(fig, sector, x_axis_time_series, y_axis_financials):
    fig.add_trace(go.Scatter(x = x_axis_time_series,
                            y = y_axis_financials,
                            mode = 'lines+markers',
                            name = sector))

def update_layout(fig, financial_indicator, financial_performance_indicators):
    return apply_standard_chart_layout(
        fig,
        title=f"Average {financial_performance_indicators.frontend_backend_string_format_mapping(financial_indicator, 'backend-to-frontend')} by Sector",
        xaxis_title="Month Year",
        yaxis_title=financial_performance_indicators.get_financial_item_unit(financial_indicator),
        legend_title="Economic sectors",
        font_size=14,
    )

