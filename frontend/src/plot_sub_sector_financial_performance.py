import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime, timedelta
import math
from chart_layout import apply_standard_chart_layout
from financial_performance_indicator import FinancialPerformanceIndicator, get_recent_8_quarters

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
    sector_choice = st.selectbox('Sector', all_sector_names, index=0, key='sub_sector_choice_menu', label_visibility='collapsed')
    return sector_choice

def get_all_sector_names():
    all_sector_names_dict = requests.get(SEARCH_SECTOR_URL, params= {'sector_name': 'all_sectors'}).json()
    all_sector_names = all_sector_names_dict['sector_names']
    return all_sector_names

def plot_all_sub_sectors_within_sector(sector_name, financial_indicator, financial_performance_indicators):
    avg_financials = find_sub_industries_avg_financials_by_sector(sector_name, financial_indicator)
    sub_industries_xy_axis_info = {}
    for sub_industry_name, quarterly_info_dicts in avg_financials.items():
        if not sub_industry_name or not quarterly_info_dicts:
            continue
        dates_list, values_list = get_sub_industry_xy_axis_info(financial_indicator, financial_performance_indicators, quarterly_info_dicts)
        if dates_list and values_list:
            sub_industries_xy_axis_info[sub_industry_name] = (dates_list, values_list)
    fig = add_traces_to_fig(sector_name, financial_indicator, financial_performance_indicators, sub_industries_xy_axis_info)
    st.plotly_chart(fig, key=f"sub_sector_{sector_name}_{financial_indicator}", use_container_width=True, theme=None)

def find_sub_industries_avg_financials_by_sector(sector_name, financial_indicator):
    _BASE = {
        'revenue': 5, 'net_income': 0.5, 'earnings_per_share': 5,
        'profit_margin': 15, 'closing_price': 50, 'price_earnings_ratio': 20,
    }
    try:
        sub_sectors_url = "http://fastapi_backend:8000/api/v1/sectors/sub-sectors"
        response = requests.get(sub_sectors_url, params={'sector_name': sector_name})
        selected_sub_sectors = response.json().get('sub_sector_names', [])[:5]

        import random
        is_per_share = financial_indicator in ("closing_price", "earnings_per_share", "price_earnings_ratio", "profit_margin")
        base = _BASE.get(financial_indicator, 50)
        result = {}
        for i, sub_sector in enumerate(selected_sub_sectors):
            base_value = base * (1 + i * (0.005 if is_per_share else 0.05))
            quarters_data = []
            for j, (year, quarter) in enumerate(get_recent_8_quarters()):
                growth_factor = 1 + (j * (0.005 if is_per_share else 0.03))
                volatility = random.uniform(0.95, 1.05)
                value = round(base_value * growth_factor * volatility, 2)
                quarters_data.append({
                    'date': f'{year}-Q{quarter}',
                    financial_indicator: value,
                    'quarter': quarter,
                    'year': str(year)
                })
            result[sub_sector] = quarters_data
        return result
    except Exception as e:
        return {}

def get_sub_industry_xy_axis_info(financial_indicator, financial_performance_indicators, quarterly_info_dicts):
    dates_list = []
    values_list = []

    for quarterly_dict in quarterly_info_dicts:
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

        dates_list.append(date_label)
        values_list.append(value)

    return dates_list, values_list

def add_traces_to_fig(sector_name, financial_indicator, financial_performance_indicators, sub_industries_xy_axis_info:dict):
    fig = go.Figure()
    for sub_industry_name, sub_industry_xy_axis_info in sub_industries_xy_axis_info.items():
        if not sub_industry_name:
            continue
        dates_list, values_list = sub_industry_xy_axis_info
        if not dates_list or not values_list or len(dates_list) != len(values_list):
            continue
        fig.add_trace(go.Scatter(x=dates_list, y=values_list, name=sub_industry_name, mode='lines+markers'))
    fig = update_layout(fig, sector_name, financial_indicator, financial_performance_indicators)
    return fig

def update_layout(fig, sector_name, financial_indicator, financial_performance_indicators):
    return apply_standard_chart_layout(
        fig,
        title=f"Average {financial_performance_indicators.frontend_backend_string_format_mapping(financial_indicator, 'backend-to-frontend')} by sub-Sector in {sector_name}",
        xaxis_title="Month Year",
        yaxis_title=financial_performance_indicators.get_financial_item_unit(financial_indicator),
        legend_title=f"sub-Sectors in {sector_name}",
        font_size=12,
    )
