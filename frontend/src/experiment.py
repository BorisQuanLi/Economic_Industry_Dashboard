import streamlit as st

def try_st_button():
    # quarterly_report_item_selected, point_in_time_item_selected = streamlit_sidebar_choices() # TBD streamlit_radio_button_choices()
    st.sidebar.header("Please select a financial indicator from")
    quarterly_report_item_selected = st.sidebar.multiselect('either time-period indicators:',
                                                        ['revenue', 'net_income', 'earnings_per_share', 'profit_margin'])
    point_in_time_item_selected = st.sidebar.multiselect('or point-in-time indicators:', ['closing_price', 'price_earnings_ratio'])
    if st.sidebar.button("Show historical financial performance:"):
        st.write(quarterly_report_item_selected)
        st.write(point_in_time_item_selected)

if __name__ == '__main__':
    try_st_button()