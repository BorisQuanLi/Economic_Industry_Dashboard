import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

SECTOR_URL = "http://127.0.0.1:5000/sectors/sector/search"
COMPANY_URL = None # to be worked out
API_URL = "http://127.0.0.1:5000/companies/company_overview/search"


def find_company_by_ticker(ticker):
    '''returns the company ticker from the web interface'''
    response = requests.get(API_URL, params = {'ticker': ticker})
    return response.json()

def find_sector(sector):
    sector_response = requests.get(SECTOR_URL, params = {'sector': sector}) 
    return sector_response.json()

sector_response = st.multiselect(
                    'Which sector are you interested in? (Select only one, please.)',
                    ['Consumer Staples', 'Health Care', 'Information Technology'],
                    ['Health Care'])
st.write('You selected:', sector_response)

companies_by_sector = find_sector(sector_response)
st.text(f"Companies in the {sector_response[0]} sector:")
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
    title=f"Quarterly revenues of companies in the {sector_response[0]} sector",
    xaxis_title="Month-Year",
    yaxis_title="Quarterly Revenue",
    legend_title="Companies",
    font=dict(
        family="Courier New, monospace",
        size=18,
        color="RebeccaPurple"
    )
)

fig.show()



