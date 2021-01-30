import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
from functools import reduce

COMPANY_URL = "http://127.0.0.1:5000/companies/company_overview/search"
SUB_INDUSTRY_URL = "http://127.0.0.1:5000/sub_industries/search"
SECTOR_URL = "http://127.0.0.1:5000/sectors/sector/search"

def find_companies_by_sub_industry(sub_industry_name):
    response = requests.get(SUB_INDUSTRY_URL, params={'sub_industry': sub_industry_name})
    response.json()

def find_company_by_ticker(ticker):
    '''returns the company ticker from the web interface'''
    response = requests.get(COMPANY_URL, params = {'ticker': ticker})
    return response.json()

def find_companies_by_sector(sector):
    selected_sector = requests.get(SECTOR_URL, params = {'sector': sector})
    return selected_sector.json()

def avg_element_wise_list(list_of_tuples: list):
    """
    Turns a list of tuples into a list of element-wise average numbers.
    """
    sum_element_wise_list = (reduce(lambda x, y: [tup[0] + tup[1] for tup in zip(x,y)], list_of_tuples) 
                                if type(list_of_tuples[0]) == tuple 
                                else list_of_tuples)
    if type(list_of_tuples[0]) == tuple:
        number_companies = len(list_of_tuples)
        return list(map(lambda sum_element_wise: sum_element_wise/ number_companies,
                            sum_element_wise_list))
    else:
        return list_of_tuples

sub_industries_selected = st.multiselect('Sub_industries:',
                        ['Hypermarkets & Super Centers', 'Pharmaceuticals', 'Technology Hardware, Storage & Peripherals'],
                        ['Hypermarkets & Super Centers', 'Pharmaceuticals', 'Technology Hardware, Storage & Peripherals'])
# find_companies_by_sub_industry(sub_industries_selected)

selected_sectors = st.multiselect(
                        'Quarterly Price/Earnings ratios by industry sectors:',
                    ['Health Care', 'Information Technology', 'Consumer Staples'],
                    ['Health Care', 'Information Technology', 'Consumer Staples'])

# plot each sector's average price/quarter-earnings ratio over 4 quarters
fig = go.Figure()
for sector in selected_sectors:
    companies_by_sector = find_companies_by_sector(sector)
    pe_list = []
    for company in companies_by_sector:
        ticker = company['ticker']
        company_info = find_company_by_ticker(ticker)
        
        pe_history = [quarter['price_earnings_ratio'] for quarter in company_info[
                                                'History of quarterly Closing Price and Price to Earnings ratios']]
        date_history = [datetime.strptime(quarter['date'], "%Y-%m-%d") for quarter in company_info[
                                                'History of quarterly Closing Price and Price to Earnings ratios']]
        pe_list.append(dict(zip(date_history, pe_history)))

    companies_pe_history_list = [company_quarterly_pe
                                        for company_pe_history_dict in pe_list 
                                                for company_quarterly_pe in company_pe_history_dict.values()]
    quarterly_average_pe_history = avg_element_wise_list(companies_pe_history_list)
    quarter_ending_dates_history = [key for key in pe_list[0].keys()] 
    

    # y, x axis, respectively, above
    # average quarterly p/e ratio trace for each sector    
    fig.add_trace(go.Scatter(x= quarter_ending_dates_history,
                            y= quarterly_average_pe_history,
                            name = f"{sector}"))

fig.update_layout(
    title=f"""Average Price/Earnings ratio by sector""",
    xaxis_title="Month-Year",
    yaxis_title="Average P/E ratio",
    legend_title="Average quarterly P/E ratio",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="RebeccaPurple"
    )
)

st.plotly_chart(fig)

selected_sectors = st.multiselect(
                    'Which sector are you interested in? (Select only one, please.)',
                    ['Health Care', 'Information Technology', 'Consumer Staples'],
                    ['Health Care', 'Information Technology', 'Consumer Staples'])

selected_sector = selected_sectors[0]
st.write(f'You selected: {selected_sector}')

companies_by_sector = find_companies_by_sector(selected_sector)
st.text(f"Companies in the {selected_sector} sector:")
st.text("=" * 30)
for company in companies_by_sector:
    st.text(f"{company['name']}   Ticker: {company['ticker']}")
    st.text(f"Year founded: {company['year_founded']}")
    st.text(f"Number of employees: {company['number_of_employees']}")
    st.text('_' * 30)


fig = go.Figure()
for company in companies_by_sector:
    ticker = company['ticker']
    company_info = find_company_by_ticker(ticker)

    revenue_history = [report['revenue'] for report in company_info['History of quarterly financials']]
    date_history = [datetime.strptime(report['date'], "%Y-%m-%d") for report in company_info['History of quarterly financials']]
    
    # https://plotly.com/python/figure-labels/
    
    fig.add_trace(go.Scatter(x=date_history,
                            y=revenue_history,
                            name = f"{company_info['name']}"))

fig.update_layout(
    title=f"""Companies in {selected_sector}:""",
    xaxis_title="Month-Year",
    yaxis_title="Quarterly Revenue",
    legend_title="Companies",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="RebeccaPurple"
    )
)

st.plotly_chart(fig)
# fig.show() -> plotly implementation, not streamlit

# Next-level choice menu

# develop a companies_by_sector method, pass in selected_sector, obtains a list of companies
# in a chosen sector, then pass it to the st.multiselect below:


# should be done in the backend, through the Flask app, not the frontend.  
companies_in_sector = [company['name'] for company in companies_by_sector]
company_response = st.multiselect(
                    f'Which company in the {selected_sector} sector are you interested in? (Select only one, please.)',
                    companies_in_sector,
                    companies_in_sector)
company_name = company_response[0]
st.write('You selected:', company_name)

def find_company_by_name(name):
    response = requests.get(COMPANY_URL, params = {'name': name})
    return response.json()

companies_by_sector = find_company_by_name(company_response)
ticker = companies_by_sector['ticker']

company_info = find_company_by_ticker(ticker)
st.text(f"Name: {company_info['name']}")
st.text(f"Ticker: {company_info['ticker']}")

revenue_history = [report['revenue'] for report in company_info['History of quarterly financials']]
date_history = [datetime.strptime(report['date'], "%Y-%m-%d") for report in company_info['History of quarterly financials']]
#fig = plt.plot(date_history, revenue_history)
#st.pyplot
#st.plotly_chart

fig = go.Figure(data=go.Scatter(x=date_history,
                             y=revenue_history))
st.plotly_chart(fig)
#plt.savefig(fig)



