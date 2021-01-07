import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

API_URL = "http://127.0.0.1:5000/companies/company_overview/search"


def find_company_by_ticker(ticker):
    '''returns the company ticker from the web interface'''
    response = requests.get(API_URL, params = {'ticker': ticker})
    return response.json()

ticker = st.selectbox("Select a company's ticker symbol:", ["AAPL", "JNJ", "PFE", "WMT"])
st.write("You selected ticker", ticker)
st.subheader('Company Information')
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
