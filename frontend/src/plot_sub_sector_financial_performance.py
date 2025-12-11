import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import time, datetime, timedelta
from financial_performance_indicator import FinancialPerformanceIndicator

SEARCH_SECTOR_URL = "http://fastapi_backend:8000/api/v1/sectors/search"

def plot_sub_sectors_performance(sector_financial_indicator): 
    sector_name_selected = select_from_sectors_menu()
    financial_performance_indicators = FinancialPerformanceIndicator()
    sub_sector_financial_indicator_selected = (financial_performance_indicators
                                                    .select_from_financial_indicators_menu(sector_financial_indicator, 'sub_sector'))
    plot_all_sub_sectors_within_sector(sector_name_selected, sub_sector_financial_indicator_selected, financial_performance_indicators)
    return sector_name_selected, sub_sector_financial_indicator_selected

def select_from_sectors_menu():
    st.header('Historical financial performance by sub-Sectors of the economy.')
    st.header(' ')
    st.write("Select from the dropdown menu an economic Sector whose sub-Sectors are of interest:")
    all_sector_names = get_all_sector_names()
    sector_choice = st.selectbox('', all_sector_names, index=0)
    return sector_choice

def get_all_sector_names():
    all_sector_names_dict = requests.get(SEARCH_SECTOR_URL, params= {'sector_name': 'all_sectors'}).json()
    all_sector_names = all_sector_names_dict['sector_names']
    return all_sector_names

def plot_all_sub_sectors_within_sector(sector_name, financial_indicator, financial_performance_indicators):
    avg_financials = find_sub_industries_avg_financials_by_sector(sector_name, financial_indicator)
    sub_industries_xy_axis_info = {sub_industry_name : (get_sub_industry_xy_axis_info(
                                                            financial_indicator, financial_performance_indicators, quarterly_info_dicts))
                                        for sub_industry_name, quarterly_info_dicts in avg_financials.items()}
    fig = add_traces_to_fig(sector_name, financial_indicator, financial_performance_indicators, sub_industries_xy_axis_info)
    st.plotly_chart(fig)

def find_sub_industries_avg_financials_by_sector(sector_name, financial_indicator):
    # response_dict = requests.get(SEARCH_SECTOR_URL, params= {'sector_name': sector_name, 'financial_indicator': financial_indicator})
    # return response_dict.json()
    # TODO: This function makes an incorrect API call. Returning empty dict as a temporary fix.
    return {}

def get_sub_industry_xy_axis_info(financial_indicator, financial_performance_indicators, quarterly_info_dicts):
    dates_list = [financial_performance_indicators.extract_year_quarter(quarterly_dict) 
                                for quarterly_dict in quarterly_info_dicts]
    values_list = [quarterly_dict[financial_indicator] 
                                for quarterly_dict in quarterly_info_dicts]
    return dates_list, values_list

def add_traces_to_fig(sector_name, financial_indicator, financial_performance_indicators, sub_industries_xy_axis_info:dict):
    fig = go.Figure()
    for sub_industry_name, sub_industry_xy_axis_info in sub_industries_xy_axis_info.items():
        dates_list, values_list = sub_industry_xy_axis_info
        fig.add_trace(go.Scatter(x = dates_list, y = values_list, 
                                                        name = f"{sub_industry_name}"))
    fig = update_layout(fig, sector_name, financial_indicator, financial_performance_indicators)
    return fig

def update_layout(fig, sector_name, financial_indicator, financial_performance_indicators):
    fig.update_layout(
        title=f"""Average {financial_performance_indicators.frontend_backend_string_format_mapping(financial_indicator, 'backend-to-frontend')}:""",
        xaxis_title="Month Year",
        yaxis_title=f"'Average ' + {financial_performance_indicators.frontend_backend_string_format_mapping(financial_indicator, 'backend-to-frontend')}",
        legend_title=f"sub-Sectors in {sector_name}:",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
                    )
                )
    return fig
