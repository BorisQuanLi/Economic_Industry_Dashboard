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
    # Get sub-sectors for the selected sector and create mock data
    try:
        sub_sectors_url = "http://fastapi_backend:8000/api/v1/sectors/sub-sectors"
        response = requests.get(sub_sectors_url)
        all_sub_sectors = response.json().get('sub_sector_names', [])
        
        # Filter to first 5 sub-sectors for demo (since we don't have sector mapping)
        selected_sub_sectors = all_sub_sectors[:5] if all_sub_sectors else []
        
        # Create 8 quarters of mock time-series data for each sub-sector
        import random
        result = {}
        for i, sub_sector in enumerate(selected_sub_sectors):
            base_value = (10 + i*5) * 1000000  # Different base values per sub-sector
            quarters_data = []
            for j, (year, quarter) in enumerate([("2023", 1), ("2023", 2), ("2023", 3), ("2023", 4), 
                                               ("2024", 1), ("2024", 2), ("2024", 3), ("2024", 4)]):
                growth_factor = 1 + (j * 0.03)  # 3% growth per quarter
                volatility = random.uniform(0.9, 1.1)  # ±10% variation
                value = int(base_value * growth_factor * volatility)
                quarters_data.append({
                    'date': f'{year}-Q{quarter}', 
                    financial_indicator: value,  # Use the actual indicator name
                    'quarter': quarter, 
                    'year': str(year)
                })
            result[sub_sector] = quarters_data
        return result
    except Exception as e:
        return {}

def get_sub_industry_xy_axis_info(financial_indicator, financial_performance_indicators, quarterly_info_dicts):
    dates_list = [financial_performance_indicators.extract_year_quarter(quarterly_dict) 
                                for quarterly_dict in quarterly_info_dicts]
    # Handle both 'revenue' and 'company_count' fields
    if quarterly_info_dicts and financial_indicator in quarterly_info_dicts[0]:
        values_list = [quarterly_dict[financial_indicator] for quarterly_dict in quarterly_info_dicts]
    else:
        # Fallback to company_count if the requested indicator doesn't exist
        values_list = [quarterly_dict.get('company_count', 0) for quarterly_dict in quarterly_info_dicts]
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
