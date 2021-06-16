import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import time, datetime, timedelta
import pandas as pd
import pandas_market_calendars as mcal
from frontend_utilities import (assemble_year_quarter, underscored_to_spaced_words_dict, 
                                frontend_backend_string_format_conversion, get_indicators_in_frontend_format)

SEARCH_SECTOR_URL = "http://127.0.0.1:5000/sectors/search"

def sub_industries_within_sector_url(sector_name):
    return f"http://127.0.0.1:5000/sectors/{sector_name}"

def plot_sub_industry_level_performance(): 
    selected_sector_name = display_all_sectors()
    done_string = 'Done. Continue to the Company level.'
    indicators_in_backend_format = ['closing_price', 'revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'price_earnings_ratio']
    indicators_in_frontend_format = get_indicators_in_frontend_format(indicators_in_backend_format)
    selected_financial_indicator = st.selectbox('', indicators_in_frontend_format, index=0)
    selected_financial_indicator = frontend_backend_string_format_conversion()[selected_financial_indicator]
    plot_all_sub_industries_in_sector(selected_sector_name, selected_financial_indicator)
    return selected_sector_name

    """
    # TBD
    selected_financial_indicator = sub_industry_first_round_choice_menu(selected_sector_name)
    if selected_financial_indicator == 'Go to the next granular level, companies within a sub-Sector.':
        return done_string, selected_sector_name
    plot_all_sub_industries_in_sector(selected_sector_name, selected_financial_indicator)
    follow_up_financial_indicator_selected = sub_industry_follow_up_choice_menu()
    if follow_up_financial_indicator_selected == 'No, go to the next granular level, companies within a sub-Sector.':
        return done_string, selected_sector_name
    """

def display_all_sectors():
    st.header('Historical financial performance by sub-Sectors of the economy.')
    st.header(' ')
    st.write("Select from the drop-down menu an economic Sector whose sub-Sectors are of interest:")

    sector_names_response = requests.get(sub_industries_within_sector_url('all_sectors'), params= {'financial_indicator': 'show all sectors'})
    sector_names = sector_names_response.json()['sector_names']
    sector_choice = st.selectbox('', sector_names, index=0)
    return sector_choice

def plot_all_sub_industries_in_sector(sector_name, financial_indicator):
    avg_financials = find_sub_industries_avg_financials_by_sector(sector_name, financial_indicator)
    sub_industries_xy_axis_info = {sub_industry_name :get_sub_industry_xy_axis_info(financial_indicator, quarterly_info_dicts)
                                        for sub_industry_name, quarterly_info_dicts in avg_financials.items()}
    fig = add_traces_to_fig(sector_name, financial_indicator, sub_industries_xy_axis_info)
    st.plotly_chart(fig)

def find_sub_industries_avg_financials_by_sector(sector_name, financial_indicator):
    response_dict = requests.get(SEARCH_SECTOR_URL, params= {'sector_name': sector_name, 'financial_indicator': financial_indicator})
    return response_dict.json()

def get_sub_industry_xy_axis_info(financial_indicator, quarterly_info_dicts):
    dates_list = [assemble_year_quarter(quarterly_dict) 
                                for quarterly_dict in quarterly_info_dicts]
    values_list = [quarterly_dict[financial_indicator] 
                                for quarterly_dict in quarterly_info_dicts]
    return dates_list, values_list

def add_traces_to_fig(sector_name, financial_indicator, sub_industries_xy_axis_info:dict):
    fig = go.Figure()
    for sub_industry_name, sub_industry_xy_axis_info in sub_industries_xy_axis_info.items():
        dates_list, values_list = sub_industry_xy_axis_info
        fig.add_trace(go.Scatter(x = dates_list, y = values_list, 
                                                        name = f"{sub_industry_name}"))
    fig = update_layout(fig, sector_name, financial_indicator)
    return fig

def update_layout(fig, sector_name, financial_indicator):
    fig.update_layout(
        title=f"""Average {underscored_to_spaced_words_dict(financial_indicator)}:""",
        xaxis_title="Month Year",
        yaxis_title=f"{'Average ' + underscored_to_spaced_words_dict(financial_indicator)}",
        legend_title=f"sub-Sectors in {sector_name}:",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
                    )
                )
    return fig
