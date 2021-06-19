import streamlit as st
import requests
import plotly.graph_objects as go
from frontend_utilities import (assemble_year_quarter, frontend_backend_string_format_conversion, 
                                get_indicators_in_frontend_format, underscored_to_spaced_words_dict)

SEARCH_SUB_SECTOR_URL = "http://127.0.0.1:5000/sub_sectors/search"

def plot_companies_performance_within_sub_sector(sector_name):
    selected_sub_sector_name = select_sub_sector_within_sector(sector_name)
    indicators_in_backend_format = ['closing_price', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'price_earnings_ratio']
    indicators_in_frontend_format = get_indicators_in_frontend_format(indicators_in_backend_format)
    selected_financial_indicator = st.selectbox('', indicators_in_frontend_format, index=0, key= 'company_level')
    selected_financial_indicator = frontend_backend_string_format_conversion()[selected_financial_indicator]
    plot_all_companies_within_sub_sector(selected_sub_sector_name, selected_financial_indicator)
    return selected_sub_sector_name

def select_sub_sector_within_sector(sector_name):
    st.header('Historical financial performance by companies within a sub-Sector.')
    st.header(' ')
    st.write(f"Select from the dropdown menu an economic sub-Sector in the {sector_name} sector:")
    sub_sector_names_response = requests.get(SEARCH_SUB_SECTOR_URL, 
                                                params= {'sub_sector_name': 'all_sub_sectors', 'financial_indicator': sector_name})
    sub_sector_names = sub_sector_names_response.json()['sub_sector_names']
    sub_sector_choice = st.selectbox('', sub_sector_names, index=0, key= 'company_level_entrypoint')
    return sub_sector_choice

def plot_all_companies_within_sub_sector(selected_sub_sector_name, selected_financial_indicator):
    avg_financials = find_company_financials_within_sub_sector(selected_sub_sector_name, selected_financial_indicator)
    sub_sectors_xy_axis_info = {company_name : get_sub_industry_xy_axis_info(selected_financial_indicator, quarterly_info_dicts)
                                        for company_name, quarterly_info_dicts in avg_financials.items()}
    fig = add_traces_to_fig(selected_sub_sector_name, selected_financial_indicator, sub_sectors_xy_axis_info)
    st.plotly_chart(fig)

def find_company_financials_within_sub_sector(sub_sector_name, financial_indicator):
    response_dict = requests.get(SEARCH_SUB_SECTOR_URL, params= {'sub_sector_name': sub_sector_name, 'financial_indicator': financial_indicator})
    return response_dict.json()

def get_sub_industry_xy_axis_info(financial_indicator, quarterly_info_dicts):
    dates_list = [assemble_year_quarter(quarterly_dict) 
                                for quarterly_dict in quarterly_info_dicts]
    values_list = [quarterly_dict[financial_indicator] 
                                for quarterly_dict in quarterly_info_dicts]
    return dates_list, values_list

def add_traces_to_fig(sub_sector_name, financial_indicator, sub_sectors_xy_axis_info:dict):
    fig = go.Figure()
    for company_name, sub_sector_xy_axis_info in sub_sectors_xy_axis_info.items():
        dates_list, values_list = sub_sector_xy_axis_info
        fig.add_trace(go.Scatter(x = dates_list, y = values_list, 
                                                        name = f"{company_name}"))
    fig = update_layout(fig, sub_sector_name, financial_indicator)
    return fig

def update_layout(fig, sub_sector_name, financial_indicator):
    fig.update_layout(
        title=f"""{underscored_to_spaced_words_dict(financial_indicator)}:""",
        xaxis_title="Month Year",
        yaxis_title=f"{underscored_to_spaced_words_dict(financial_indicator)}",
        legend_title=f"Companies in {sub_sector_name}:",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
                    )
                )
    return fig
