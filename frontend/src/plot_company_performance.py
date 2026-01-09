import streamlit as st
import requests
import plotly.graph_objects as go
import math
from chart_layout import apply_standard_chart_layout
from financial_performance_indicator import FinancialPerformanceIndicator
from config import BACKEND_BASE_URL

def select_sub_sector_within_sector(sub_sector_name):
    st.header('Historical financial performance by companies within a sub-Sector.')
    st.header(' ')
    st.write(f"Select from the dropdown menu an economic sub-Sector in the {sub_sector_name} sector:")
    sub_sector_names_response = requests.get(SEARCH_SUB_SECTOR_URL,
                                                params={'sector_name': sub_sector_name})
    sub_sector_names = sub_sector_names_response.json()['sub_sector_names']
    sub_sector_choice = st.selectbox('Sub-Sector', sub_sector_names, index=0, key=f'company_level_{sub_sector_name}', label_visibility='collapsed')
    return sub_sector_choice

def plot_all_companies_within_sub_sector(selected_sub_sector_name, selected_financial_indicator, financial_performance_indicators):
    avg_financials = find_company_financials_within_sub_sector(selected_sub_sector_name, selected_financial_indicator)
    if not avg_financials:
        return
    sub_sectors_xy_axis_info = {}
    for company_name, quarterly_info_dicts in avg_financials.items():
        if not company_name or not quarterly_info_dicts:
            continue
        dates_list, values_list = get_sub_industry_xy_axis_info(
            selected_financial_indicator,
            financial_performance_indicators,
            quarterly_info_dicts,
        )
        if dates_list and values_list:
            sub_sectors_xy_axis_info[str(company_name)] = (dates_list, values_list)

    fig = add_traces_to_fig(selected_sub_sector_name, selected_financial_indicator, financial_performance_indicators, sub_sectors_xy_axis_info)
    st.plotly_chart(fig, key=f"company_{selected_sub_sector_name}_{selected_financial_indicator}", use_container_width=True, theme=None)

def find_company_financials_within_sub_sector(sub_sector_name, financial_indicator):
    try:
        company_financials_url = f"{BACKEND_BASE_URL}/api/v1/sectors/companies/{sub_sector_name}/financials"
        response = requests.get(company_financials_url, params={'financial_indicator': financial_indicator})
        companies = response.json()
        if not companies:
            st.warning("No company data found. Please ensure the ETL pipeline has run.")
            return {}
        return companies
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

def add_traces_to_fig(sub_sector_name, financial_indicator, financial_performance_indicators, sub_sectors_xy_axis_info:dict):
    fig = go.Figure()
    for company_name, sub_sector_xy_axis_info in sub_sectors_xy_axis_info.items():
        if not company_name:
            continue
        dates_list, values_list = sub_sector_xy_axis_info
        if not dates_list or not values_list or len(dates_list) != len(values_list):
            continue
        fig.add_trace(go.Scatter(x = dates_list, y = values_list, 
                                                        name = f"{company_name}", mode='lines+markers'))
    fig = update_layout(fig, sub_sector_name, financial_indicator, financial_performance_indicators)
    return fig

def update_layout(fig, sub_sector_name, financial_indicator, financial_performance_indicators):
    return apply_standard_chart_layout(
        fig,
        title=f"Average {financial_performance_indicators.frontend_backend_string_format_mapping(financial_indicator, 'backend-to-frontend')} by company in {sub_sector_name}",
        xaxis_title="Month Year",
        yaxis_title=financial_performance_indicators.get_financial_item_unit(financial_indicator),
        legend_title=f"Companies in {sub_sector_name}",
        font_size=12,
    )

def plot_company_level_performance(sub_sector_name, financial_indicator):
    from financial_performance_indicator import FinancialPerformanceIndicator
    financial_performance_indicators = FinancialPerformanceIndicator()
    selected_sub_sector = select_sub_sector_within_sector(sub_sector_name)
    plot_all_companies_within_sub_sector(selected_sub_sector, financial_indicator, financial_performance_indicators)
