import streamlit as st
import requests
import plotly.graph_objects as go
from helpers import unpack_year_quarter, get_financial_item_unit

CROSS_SECTORS_URL = "http://127.0.0.1:5000/sectors"

def plot_sectors_performance():
    st.title('Historical financial performance by economic sectors.')
    st.title(' ')
    financial_items_selected = st.multiselect('Please select a financial-statement item:',
                                                ['revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'closing_price', 'price_earnings_ratio'],
                                                ['revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'closing_price', 'price_earnings_ratio'])
    plot_selected_financial_items(financial_items_selected)

def plot_selected_financial_items(financial_items_selected):
    for financial_item in financial_items_selected:
        fig = go.Figure()
        get_plotly_chart_data(fig, financial_item)
        update_layout(fig, financial_item)
        st.plotly_chart(fig, use_container_width= True)

def find_sector_avg_financials(financial_item):
    response_dict = requests.get(CROSS_SECTORS_URL, params= {'financial_item': financial_item})
    return response_dict.json()

def get_time_n_financials_axis(sector, quarterly_financials, financial_item):
    try:
        x_axis_time_series = [unpack_year_quarter(year_quarter) for year_quarter in quarterly_financials.keys()]
        y_axis_financials = [(financials[f'avg_{financial_item}']) for financials in quarterly_financials.values()]
    except Exception as e:
        print(e)
        breakpoint()
    return x_axis_time_series, y_axis_financials

def add_trace(fig, sector, x_axis_time_series, y_axis_financials):
    fig.add_trace(go.Scatter(x = x_axis_time_series,
                            y = y_axis_financials,
                            mode = 'lines',
                            name = sector))

def get_plotly_chart_data(fig, financial_item):
    quarterly_financial_history_by_sector = find_sector_avg_financials(financial_item)
    for sector, quarterly_financials in quarterly_financial_history_by_sector.items():
        # feed these add to st.add_trace()
        x_axis_time_series, y_axis_financials = get_time_n_financials_axis(sector,
                                                                            quarterly_financials,
                                                                            financial_item)
        add_trace(fig, sector, x_axis_time_series, y_axis_financials)

def update_layout(fig, financial_item):
    return fig.update_layout(
                                title= f"Average {financial_item}",
                                xaxis_title="Year-Quarter",
                                yaxis_title= get_financial_item_unit(financial_item),
                                legend_title="Economic sectors",
                                font=dict(
                                            family="Courier New, monospace",
                                            size=18,
                                            color="RebeccaPurple"
                                        )
                            )

