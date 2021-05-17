import streamlit as st
import requests
import plotly.graph_objects as go
from plot_sub_industry_financials import plot_avg_financial_sub_industries
from plot_sector_financials import plot_sectors_performance
from helpers import (beautify_streamlit_presentation, welcome_message, provide_financial_indicator_choice_menu,
                     underscored_to_spaced_words_dict, spaced_to_underscored_words_dict)

SEARCH_COMPANY_URL = "http://127.0.0.1:5000/companies/company_overview/search"
SEARCH_SUB_INDUSTRY_URL = "http://127.0.0.1:5000/sub_industries/search"

welcome_message()
# beautify_streamlit_presentation()

# present each sub-industry's average financials within a particular sector (after sector name is entered in the url)
AGGREGATION_BY_SECTOR_URL = "http://127.0.0.1:5000/sectors"

plot_sectors_performance()
breakpoint()

# radio button
sector_selected = st.radio("Which economic sector's performance are your interested in?",
                            [' ', 'Consumer Staples', 'Energy', 'Healthcare']) # sector names hard-coded for now 
st.write(f"You selected: {sector_selected}")

# Historical financial performance by sub-industries within an economic sector.
st.title("Historical financial performance by sub-industries within an economic sector.")
st.title(" ")
SEARCH_SECTOR_URL = "http://127.0.0.1:5000/sectors/search"
plot_avg_financial_sub_industries('Consumer Staples', 'revenue')
plot_avg_financial_sub_industries('Consumer Staples', 'profit_margin')
plot_avg_financial_sub_industries('Energy', 'profit_margin')
plot_avg_financial_sub_industries('Energy', 'revenue')


# plot company-level financial history. Move to a separate module.
st.title("Historical financial performance by companies within a sub-industry.")
st.title(" ")
from datetime import datetime
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
breakpoint()
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

