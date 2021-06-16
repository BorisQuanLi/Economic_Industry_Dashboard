import streamlit as st
import requests
import plotly.graph_objects as go
from frontend_utilities import (assemble_year_quarter, get_financial_item_unit, underscored_to_spaced_words_dict)
from choice_menus import sector_level_first_round_choice_menu, sector_level_follow_up_choice_menu

def companies_within_sub_sector_url(sub_sector_name):
    return f"http://127.0.0.1:5000/sub_industries/{sub_sector_name}"

def plot_companies_performance_within_sub_sector(sector_name):
    selected_company_name = display_all_sub_sectors(sector_name)
    breakpoint()

    plot_selected_financial_indicator('price_earnings_ratio')
    selected_financial_indicator = sector_level_first_round_choice_menu()
    if selected_financial_indicator == 'Go to the next granular level, sub-Sectors within an economic Sector.':
        return 'Done. Continue to the Sub-Industry level.'
    plot_selected_financial_indicator(selected_financial_indicator)
    follow_up_financial_indicator_selected = sector_level_follow_up_choice_menu()
    if follow_up_financial_indicator_selected == 'No, go to the next granular level, sub-Sectors within an economic Sector.':   
        return 'Done. Continue to the Sub-Industry level.'

def display_all_sub_sectors(sector_name):
    st.header('Historical financial performance by companies within a sub-Sector.')
    sub_sector_names_response = requests.get(companies_within_sub_sector_url('all_sub_industries'),
                                                    params= {'financial_indicator': sector_name})
    breakpoint()
    sub_sector_names = sub_sector_names_response.json()['sub_sector_names']
    selection_instruction = "Select from this pull-down menu an economic sub-Sector whose companies are of interest:"
    sub_sector_choice = st.selectbox('', [selection_instruction] + sub_sector_names, index=0)
    if sub_sector_choice == selection_instruction:
        st.stop()
    return sub_sector_choice

def plot_selected_financial_indicator(financial_indicator):
    fig = go.Figure()
    get_plotly_chart_data(fig, financial_indicator)
    update_layout(fig, financial_indicator)
    st.plotly_chart(fig, use_container_width= True)

def get_plotly_chart_data(fig, financial_indicator):
    try:
        quarterly_financial_history_by_sector = find_sector_avg_financials(financial_indicator)
        for sector, quarterly_financials in quarterly_financial_history_by_sector.items():
            x_axis_time_series, y_axis_financials = get_time_n_financials_axis(sector,
                                                                                quarterly_financials,
                                                                                financial_indicator)
            add_trace(fig, sector, x_axis_time_series, y_axis_financials)
    except Exception as e:
        print(e)
        print(quarterly_financial_history_by_sector)
        breakpoint()

def find_sector_avg_financials(financial_indicator):
    response_dict = requests.get(AGGREGATION_BY_SECTOR_URL, params= {'financial_indicator': financial_indicator})
    return response_dict.json()

def get_time_n_financials_axis(sector, quarterly_financials, financial_indicator):
    x_axis_time_series = [assemble_year_quarter(quarterly_dict) for quarterly_dict in quarterly_financials]
    y_axis_financials = [quarterly_dict[financial_indicator] for quarterly_dict in quarterly_financials]
    return x_axis_time_series, y_axis_financials

def add_trace(fig, sector, x_axis_time_series, y_axis_financials):
    fig.add_trace(go.Scatter(x = x_axis_time_series,
                            y = y_axis_financials,
                            mode = 'lines',
                            name = sector))

def update_layout(fig, financial_indicator):
    return fig.update_layout(
                                title= f"{underscored_to_spaced_words_dict(financial_indicator)} (Average)",
                                yaxis_title= get_financial_item_unit(financial_indicator),
                                legend_title="Economic sectors",
                                font=dict(
                                            family="Courier New, monospace",
                                            size=18,
                                            color="RebeccaPurple"
                                        )
                            )

