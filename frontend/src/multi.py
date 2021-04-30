import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import time, datetime, timedelta
import pandas as pd
import pandas_market_calendars as mcal

SEARCH_COMPANY_URL = "http://127.0.0.1:5000/companies/company_overview/search"
SEARCH_SUB_INDUSTRY_URL = "http://127.0.0.1:5000/sub_industries/search"
SEARCH_SECTOR_URL = "http://127.0.0.1:5000/sectors/search"
SECTOR_URL = "http://127.0.0.1:5000/sectors/<sector_name>"

# present each sub-industry's average financials within a particular sector (after sector name is entered in the url)

def find_sub_industries_avg_financials_by_sector(sector_name, financial_item):
    response_dict = requests.get(SEARCH_SECTOR_URL, params= {'sector_name': sector_name,
                                                             'financial_item': financial_item})
    return response_dict.json()

# plotly chart
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
    dates_list = [get_quarter_end_date_str(year_quarter) 
                                            for year_quarter in sub_industry_xy_axis_info[1]]
    return sub_industry_name, dates_list, values_list

def get_quarter_end_trading_day(year_quarter_str:str):
    end_date_str = get_quarter_end_date_str(year_quarter_str)
    start_date = datetime.strptime(end_date_str, '%Y-%m-%d') - timedelta(days= 5)
    start_date_str = datetime.strftime(start_date, '%Y-%m-%d')
    nyse = mcal.get_calendar('NYSE')
    days_range = nyse.valid_days(start_date= start_date_str, end_date= end_date_str)
    quarter_end_trading_day = days_range[-1].date()
    return quarter_end_trading_day

def get_quarter_end_date_str(year_quarter_str:str):
    year_str = year_quarter_str.split('-')[0]
    quarter_str = year_quarter_str.split('-')[1]
    quarter_ending_date_dict = {'01': '03-31', '02': '06-30', '03': '09-30', '04': '12-31'}
    end_date_str = year_str + '-' + quarter_ending_date_dict[quarter_str]
    return end_date_str

def update_layout(fig, sector_name, financial_item):
    fig.update_layout(
        title=f"""Sub-industries in the {sector_name} sector:""", # change title
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

def plot_avg_financial_sub_industries(sector_name, financial_item):
    avg_financials = find_sub_industries_avg_financials_by_sector(sector_name, financial_item)
    sub_industries_xy_axis_info = [get_sub_industry_xy_axis_info(sub_industry_name, attr_list)
                                        for sub_industry_name, attr_list in avg_financials.items()]
    fig = add_traces_to_fig(f'{sector_name}', f'{financial_item}', sub_industries_xy_axis_info)
    st.plotly_chart(fig)

plot_avg_financial_sub_industries('Consumer Staples', 'revenue')
plot_avg_financial_sub_industries('Consumer Staples', 'profit_margin')
plot_avg_financial_sub_industries('Energy', 'profit_margin')
plot_avg_financial_sub_industries('Energy', 'revenue')



def find_company_info(selected_company_name):
    response = requests.get(SEARCH_COMPANY_URL, params= {'company_name': selected_company_name})
    return response.json()

def extract_company_info(company_info:dict):
    # get only the most recent quarter's financials
    company_info = {k:v for k, v in company_info.items()
                            if k not in ['id', 'sub_industry_id', 'HQ_state']}
    company_info['Quarterly_financials'] = [extract_financials_dict(quarterly_financials)
                                                for quarterly_financials in company_info['Quarterly_financials']]
    company_info['Closing_prices_and_P/E_ratio'] = [extract_price_pe_dict(quarterly_price_pe)
                                                        for quarterly_price_pe in company_info['Closing_prices_and_P/E_ratio']]
    return company_info

def extract_financials_dict(quarterly_financials:dict):
    extracted_financials_dict =  {k:v for k, v in quarterly_financials.items()
                                                        if k not in ['id', 'company_id']}
    return extracted_financials_dict

def extract_price_pe_dict(quarterly_price_pe:dict):
    extracted_price_pe_dict = {k:v for k, v in quarterly_price_pe.items()
                                                                if k not in ['id', 'company_id']}
    return extracted_price_pe_dict

def st_text_companies_info(companies_info:list):
    for company_info in companies_info:
        st_text(company_info)
    
def st_text(streamlined_company_info:dict):
    for k, v in streamlined_company_info.items():
        if k == ['Quarterly_financials']:
            st.text(k)
            for key, value in v:
                st.text(key)
                st.text(value)
        elif k == ['Closing_prices_and_P/E_ratio']:
            st.text(k)
            for key, value in v:
                st.text(key)
                st.text(value)
        else:
            st.text(k)
            st.text(v)

def get_xy_axis_values(company_info):
    company_name = company_info['name']
    revenue_history = [report['revenue'] for report in company_info['Quarterly_financials']]
    date_history = [datetime.strptime(report['date'], "%Y-%m-%d") for report 
                                        in company_info['Quarterly_financials']]
    return company_name, revenue_history, date_history

def add_traces_to_fig(companies_xy_axis_values:list):
    company_names, revenue_histories, dates_str = unpack_values(companies_xy_axis_values)
    fig = go.Figure()
    for company_name, company_rev_history in zip(company_names, revenue_histories):
        fig.add_trace(go.Scatter(x = dates_str, y = company_rev_history, 
                                                        name = f"{company_name}"))
    fig = update_layout(fig)
    return fig

def unpack_values(companies_xy_axis_values):
    company_names = [name for name, revenue, dates in companies_xy_axis_values]
    revenue_histories = [revenue for name, revenue, dates in companies_xy_axis_values]
    dates_history = [dates for name, revenue, dates in companies_xy_axis_values][0]
    dates_str = [datetime.strftime(date.date(), '%Y-%m-%d')
                                                    for date in dates_history]
    return company_names, revenue_histories, dates_str

def update_layout(fig):

    # go.Figure(data=[])
    # st.plotly_chart(fig)
    # https://plotly.com/python/figure-labels/

    fig.update_layout(
        title=f"""Companies in the Energy sector:""", # change title
        xaxis_title="Month-Year",
        yaxis_title="Quarterly Revenue",
        legend_title="Companies",
        font=dict(
            family="Courier New, monospace",
            size=18,
            color="RebeccaPurple"
                    )
                )
    return fig



selected_company_name = st.multiselect(f"Please select an Energy company: ",
                                    ['Valero Energy', 'Phillips 66', 'Chevron Corp.', 'Exxon Mobil Corp.'],
                                    ['Valero Energy', 'Phillips 66', 'Chevron Corp.', 'Exxon Mobil Corp.'])
st.write(selected_company_name)
companies_info = find_company_info(selected_company_name)
extracted_companies_info = [extract_company_info(company_info) 
                                                    for company_info in companies_info]
# print text info to screen:
# st_text_companies_info(extracted_companies_info)

# plotly plot
companies_xy_axis_values = [get_xy_axis_values(company_info) 
                                                for company_info in extracted_companies_info]
fig = add_traces_to_fig(companies_xy_axis_values)
st.plotly_chart(fig)
   
st.write("Data provided by Financial Modeling Prep:")
st.write("https://financialmodelingprep.com/developer/docs/")
# fig.show() -> plotly implementation, not streamlit

