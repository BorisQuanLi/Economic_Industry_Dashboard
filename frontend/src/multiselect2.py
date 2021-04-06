
selected_sectors = st.multiselect(
                        'Quarterly Price/Earnings ratios by industry sectors:',
                    ['Health Care', 'Information Technology', 'Consumer Staples'],
                    ['Health Care', 'Information Technology', 'Consumer Staples'])

# plot each sector's average price/quarter-earnings ratio over 4 quarters
fig = go.Figure()
for sector in selected_sectors:
    if sector != 'Health Care':
        # need to first populate the tables with companies other than those in Health Care.
        continue  
    companies_by_sector = find_companies_by_sector(sector)
    pe_list = []
    for company in companies_by_sector:
        ticker = company['ticker']
        company_info = find_company_by_ticker(ticker)
        pe_history = [quarter['price_earnings_ratio'] for quarter in company_info[
                                                'Quarterly Closing Price and P/E ratio']]
        date_history = [datetime.strptime(quarter['date'], "%Y-%m-%d") for quarter in company_info[
                                                'Quarterly Closing Price and P/E ratio']]
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

