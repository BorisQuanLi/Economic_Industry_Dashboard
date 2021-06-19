import streamlit as st
import requests
import plotly.graph_objects as go
from plot_sub_industry_financial_performance import plot_sub_industry_level_performance
from plot_sector_financial_performance import plot_sector_level_performance
from plot_company_performance import plot_companies_performance_within_sub_sector
from frontend_utilities import welcome_message

welcome_message()

plot_sector_level_performance()
sector_name = plot_sub_industry_level_performance()
plot_companies_performance_within_sub_sector(sector_name)
st.write("Data provided by Financial Modeling Prep:")
st.write("https://financialmodelingprep.com/developer/docs/")
st.stop()

