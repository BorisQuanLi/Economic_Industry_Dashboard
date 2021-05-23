import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import time, datetime, timedelta
import pandas as pd
import pandas_market_calendars as mcal
from choice_menus import sub_industry_first_round_choice_menu, sub_industry_follow_up_choice_menu
from frontend_utilities import (assemble_year_quarter, get_financial_item_unit,
                    underscored_to_spaced_words_dict, spaced_to_underscored_words_dict)

def sub_industry_within_sector_url(sector_name):
    return f"http://127.0.0.1:5000/sectors/{sector_name}/"

def plot_sub_industry_level_performance(): #sector_name, financial_indicator  
    selected_sector_name = display_all_sectors()
    plot_all_sub_industries_in_sector(selected_sector_name, 'price_earnings_ratio')
    selected_financial_indicator = sub_industry_first_round_choice_menu(selected_sector_name)
    plot_all_sub_industries_in_sector(selected_sector_name, selected_financial_indicator)
    follow_up_financial_indicator_selected = sub_industry_follow_up_choice_menu()

    breakpoint()

def display_all_sectors():
    st.header('Historical financial performance by sub-industries.')
    sector_names_response = requests.get(sub_industry_within_sector_url('all_sectors'), params= {'financial_indicator': 'show all sectors'})
    sector_names = sector_names_response.json()['sector_names']
    selection_instruction = "Please select from this pull-down menu a Sector whose Sub-Industries are of interest:"
    sector_choice = st.selectbox('', [selection_instruction] + sector_names, index=0)
    if sector_choice == selection_instruction:
        st.stop()
    return sector_choice

def plot_all_sub_industries_in_sector(sector_name, financial_indicator):
    avg_financials = find_sub_industries_avg_financials_by_sector(sector_name, financial_indicator)
    sub_industries_xy_axis_info = {sub_industry_name :get_sub_industry_xy_axis_info(financial_indicator, quarterly_info_dicts)
                                        for sub_industry_name, quarterly_info_dicts in avg_financials.items()}
    fig = add_traces_to_fig(sector_name, financial_indicator, sub_industries_xy_axis_info)
    st.plotly_chart(fig)

def find_sub_industries_avg_financials_by_sector(sector_name, financial_indicator):
    url = sub_industry_within_sector_url(sector_name)
    response_dict = requests.get(url, params= {'financial_indicator': financial_indicator})
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
        title=f"""Avg. {financial_indicator} of sub-industries in the {sector_name} sector:""",
        xaxis_title="Month Year",
        yaxis_title=f"{'Average ' + ' '.join([i.capitalize() for i in financial_indicator.split('_')])}",
        legend_title="Sub Industries:",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
                    )
                )
    return fig


