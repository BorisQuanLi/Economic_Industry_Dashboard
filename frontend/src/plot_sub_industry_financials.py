import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import time, datetime, timedelta
import pandas as pd
import pandas_market_calendars as mcal
from helpers import (unpack_year_quarter, get_financial_item_unit,
                    underscored_to_spaced_words_dict, spaced_to_underscored_words_dict)

SEARCH_SECTOR_URL = "http://127.0.0.1:5000/sectors/search"

def plot_avg_financial_sub_industries(sector_name, financial_item):
    avg_financials = find_sub_industries_avg_financials_by_sector(sector_name, financial_item)
    sub_industries_xy_axis_info = [get_sub_industry_xy_axis_info(sub_industry_name, attr_list)
                                        for sub_industry_name, attr_list in avg_financials.items()]
    fig = add_traces_to_fig(sector_name, financial_item, sub_industries_xy_axis_info)
    st.plotly_chart(fig)

def find_sub_industries_avg_financials_by_sector(sector_name, financial_item):
    response_dict = requests.get(SEARCH_SECTOR_URL, params= {'sector_name': sector_name,
                                                             'financial_item': financial_item})
    return response_dict.json()

def get_sub_industry_xy_axis_info(sub_industry_name, attr_list):
    avg_financial_item_name = attr_list[-1]
    dates_list = list(attr_list[0][avg_financial_item_name].keys())
    values_list = list(attr_list[0][avg_financial_item_name].values())
    return sub_industry_name, dates_list, values_list

def add_traces_to_fig(sector_name, financial_item, sub_industries_xy_axis_info:list):
    fig = go.Figure()
    for sub_industry_xy_axis_info in sub_industries_xy_axis_info:
        sub_industry_name, dates_list, values_list = unpack_info(sub_industry_xy_axis_info)
        fig.add_trace(go.Scatter(x = dates_list, y = values_list, 
                                                        name = f"{sub_industry_name}"))
    fig = update_layout(fig, sector_name, financial_item)
    return fig

def unpack_info(sub_industry_xy_axis_info):
    sub_industry_name, values_list = sub_industry_xy_axis_info[0], sub_industry_xy_axis_info[2]
    dates_list = [unpack_year_quarter(year_quarter) 
                                            for year_quarter in sub_industry_xy_axis_info[1]]
    return sub_industry_name, dates_list, values_list

def update_layout(fig, sector_name, financial_item):
    fig.update_layout(
        title=f"""Sub-industries in the {sector_name} sector:""",
        xaxis_title="Month Year",
        yaxis_title=f"{'Average ' + ' '.join([i.capitalize() for i in financial_item.split('_')])}",
        legend_title="Sub Industries:",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
                    )
                )
    return fig


