import streamlit as st
import requests
import plotly.graph_objects as go
from financial_performance_indicator import FinancialPerformanceIndicator

SEARCH_SUB_SECTOR_URL = "http://fastapi_backend:8000/api/v1/sectors/sub-sectors"

def plot_company_level_performance(sub_sector_name, sub_sector_financial_indicator):
    selected_sub_sector_name = select_sub_sector_within_sector(sub_sector_name)
    financial_performance_indicators = FinancialPerformanceIndicator()
    selected_financial_indicator = (financial_performance_indicators
                                        .select_from_financial_indicators_menu(sub_sector_financial_indicator, 'company'))
    plot_all_companies_within_sub_sector(selected_sub_sector_name, selected_financial_indicator, financial_performance_indicators)
    return selected_sub_sector_name

def select_sub_sector_within_sector(sub_sector_name):
    st.header('Historical financial performance by companies within a sub-Sector.')
    st.header(' ')
    st.write(f"Select from the dropdown menu an economic sub-Sector in the {sub_sector_name} sector:")
    sub_sector_names_response = requests.get(SEARCH_SUB_SECTOR_URL, 
                                                params= {'sub_sector_name': 'all_sub_sectors', 'financial_indicator': sub_sector_name})
    sub_sector_names = sub_sector_names_response.json()['sub_sector_names']
    sub_sector_choice = st.selectbox('', sub_sector_names, index=0, key= 'company_level_entrypoint')
    return sub_sector_choice

def plot_all_companies_within_sub_sector(selected_sub_sector_name, selected_financial_indicator, financial_performance_indicators):
    avg_financials = find_company_financials_within_sub_sector(selected_sub_sector_name, selected_financial_indicator)
    sub_sectors_xy_axis_info = {company_name : (get_sub_industry_xy_axis_info(
                                                    selected_financial_indicator, financial_performance_indicators, quarterly_info_dicts))
                                        for company_name, quarterly_info_dicts in avg_financials.items()}
    fig = add_traces_to_fig(selected_sub_sector_name, selected_financial_indicator, financial_performance_indicators, sub_sectors_xy_axis_info)
    st.plotly_chart(fig)

def find_company_financials_within_sub_sector(sub_sector_name, financial_indicator):
    try:
        company_financials_url = f"http://fastapi_backend:8000/api/v1/sectors/companies/{sub_sector_name}/financials"
        response = requests.get(company_financials_url, params={'financial_indicator': financial_indicator})
        return response.json()
    except Exception as e:
        return {}

def get_sub_industry_xy_axis_info(financial_indicator, financial_performance_indicators, quarterly_info_dicts):
    dates_list = [financial_performance_indicators.extract_year_quarter(quarterly_dict) 
                                            for quarterly_dict in quarterly_info_dicts]
    # Handle both 'revenue' and other field names
    if quarterly_info_dicts and financial_indicator in quarterly_info_dicts[0]:
        values_list = [quarterly_dict[financial_indicator] for quarterly_dict in quarterly_info_dicts]
    else:
        # Fallback to first numeric field found
        first_dict = quarterly_info_dicts[0] if quarterly_info_dicts else {}
        numeric_fields = [k for k, v in first_dict.items() if isinstance(v, (int, float))]
        if numeric_fields:
            field = numeric_fields[0]
            values_list = [quarterly_dict.get(field, 0) for quarterly_dict in quarterly_info_dicts]
        else:
            values_list = [0] * len(quarterly_info_dicts)
    return dates_list, values_list

def add_traces_to_fig(sub_sector_name, financial_indicator, financial_performance_indicators, sub_sectors_xy_axis_info:dict):
    fig = go.Figure()
    for company_name, sub_sector_xy_axis_info in sub_sectors_xy_axis_info.items():
        dates_list, values_list = sub_sector_xy_axis_info
        fig.add_trace(go.Scatter(x = dates_list, y = values_list, 
                                                        name = f"{company_name}"))
    fig = update_layout(fig, sub_sector_name, financial_indicator, financial_performance_indicators)
    return fig

def update_layout(fig, sub_sector_name, financial_indicator, financial_performance_indicators):
    fig.update_layout(
        title=f"""{financial_performance_indicators.frontend_backend_string_format_mapping(financial_indicator, 'backend-to-frontend')}:""",
        xaxis_title="Month Year",
        yaxis_title=f"{financial_performance_indicators.frontend_backend_string_format_mapping(financial_indicator, 'backend-to-frontend')}",
        legend_title=f"Companies in {sub_sector_name}:",
        font=dict(
            family="Courier New, monospace",
            size=12,
            color="RebeccaPurple"
                    )
                )
    return fig
