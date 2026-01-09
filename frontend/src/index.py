import streamlit as st
st.set_page_config(layout="wide")
from datetime import datetime
from plot_sub_sector_financial_performance import plot_sub_sectors_performance
from plot_sector_financial_performance import plot_sector_level_performance
from plot_company_performance import plot_company_level_performance
from components.ai_insights import render_ai_insights_placeholder

st.title("Welcome to the Economic Analysis api, through the prism of the S&P 500 stocks performance.")
st.title(" ")
st.write(f"                           by Boris Li, {datetime.now().year}")

financial_indicator_selected = plot_sector_level_performance()
sub_sector_name, sub_sector_financial_indicator = plot_sub_sectors_performance(financial_indicator_selected)
# plot_company_level_performance(sub_sector_name, sub_sector_financial_indicator)

st.write("Data provided by Financial Modeling Prep:")
st.write("https://financialmodelingprep.com/developer/docs/")

render_ai_insights_placeholder()
