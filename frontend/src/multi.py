import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime

COMPANY_URL = "http://127.0.0.1:5000/companies/company_overview/search"
SUB_INDUSTRY_URL = "http://127.0.0.1:5000/sub_industries/search"
SECTOR_URL = "http://127.0.0.1:5000/sectors/sector/search"

def find_company_info(selected_company_name:str):
    response = requests.get(COMPANY_URL, params= {'company_name': selected_company_name})
    return response.json()

def streamline_company_info(company_info:dict):
    # get only the most recent quarter's financials
    company_info = {k:v for k, v in company_info.items()
                            if k not in ['id', 'sub_industry_id', 'HQ_state']}
    company_info['Quarterly financials'] = company_info['Quarterly financials'][0]
    company_info['Quarterly financials'] = {k:v for k, v in company_info['Quarterly financials'].items()
                                                        if k not in ['id', 'company_id']}
    company_info['Quarterly Closing Price and P/E ratio'] = company_info['Quarterly Closing Price and P/E ratio'][0]
    company_info['Quarterly Closing Price and P/E ratio'] = {k:v for k, v in 
                                                                        company_info['Quarterly Closing Price and P/E ratio'].items()
                                                                        if k not in ['id', 'company_id']}
    return company_info

def st_text_company_info(streamline_company_info):
    for k, v in streamlined_company_info.items():
        if k == ['Quarterly financials']:
            st.text(k)
            for key, value in v:
                st.text(key)
                st.text(value)
        elif k == ['Quarterly Closing Price and P/E ratio']:
            st.text(k)
            for key, value in v:
                st.text(key)
                st.text(value)
        else:
            st.text(k)
            st.text(v)

selected_company_name = st.multiselect("Please select a Health Care company: ",
                                    ['Amgen Inc.', 'Biogen Inc.', 'Anthem', 'Cigna'],
                                    ['Amgen Inc.', 'Biogen Inc.', 'Anthem', 'Cigna'])
st.write(selected_company_name)
company_info = find_company_info(selected_company_name)
streamlined_company_info = streamline_company_info(company_info)
# print text info to screen:
st_text_company_info(streamline_company_info)

# plotly plot

revenue_history = [report['revenue'] for report 
                                    in company_info['Quarterly financials']]
date_history = [datetime.strptime(report['date'], "%Y-%m-%d") for report 
                                    in company_info['Quarterly financials']]

fig = go.Figure(data=go.Scatter(x=date_history,
                             y=revenue_history))
st.plotly_chart(fig)

# https://plotly.com/python/figure-labels/

fig.add_trace(go.Scatter(x=date_history,
                        y=revenue_history,
                        name = f"{company_info['name']}"))

fig.update_layout(
    title=f"""Companies in {company_info['name']}:""",
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


