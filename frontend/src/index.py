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
st.stop()
plot_companies_performance_within_sub_sector(sector_name)
st.write("Data provided by Financial Modeling Prep:")
st.write("https://financialmodelingprep.com/developer/docs/")
st.stop()
breakpoint()

# TBD
plot_sector_status = plot_sector_level_performance()
if plot_sector_status == 'Done. Continue to the sub-Sector level.':
    plot_sub_industry_status, sector_name = plot_sub_industry_level_performance()
    if plot_sub_industry_status == 'Done. Continue to the Company level.':
        plot_companies_performance_within_sub_sector(sector_name)
else:
    breakpoint()
   
st.write("Data provided by Financial Modeling Prep:")
st.write("https://financialmodelingprep.com/developer/docs/")
# fig.show() -> plotly implementation, not streamlit

