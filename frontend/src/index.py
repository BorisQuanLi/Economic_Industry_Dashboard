import streamlit as st
import requests
import plotly.graph_objects as go
from plot_sub_sector_financial_performance import plot_sub_sectors_performance
from plot_sector_financial_performance import plot_sector_level_performance
from plot_company_performance import plot_company_level_performance

st.title("Welcome to the Economic Analysis api, through the prism of the S&P 500 stocks performance.")
st.title(" ")
st.write("                           by Boris Li, 2021")

financial_indicator_selected = plot_sector_level_performance()
sub_sector_name, sub_sector_financial_indicator = plot_sub_sectors_performance(financial_indicator_selected)
plot_company_level_performance(sub_sector_name, sub_sector_financial_indicator)

st.write("Data provided by Financial Modeling Prep:")
st.write("https://financialmodelingprep.com/developer/docs/")
st.stop()

