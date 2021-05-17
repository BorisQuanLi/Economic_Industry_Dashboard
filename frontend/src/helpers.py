import streamlit as st

def beautify_streamlit_presentation():
    # Disable any default selection of a Streamlit Radio button group.  To be moved to helpers.py?
    # https://discuss.streamlit.io/t/radio-button-group-with-no-selection/3229/7
    st.markdown(
        """ <style>
                div[role="radiogroup"] >  :first-child{
                    display: none !important;
                }
            </style>
            """,
        unsafe_allow_html=True
    )

    # make the Raido button group horizontal.  https://discuss.streamlit.io/t/horizontal-radio-buttons/2114/3
    st.write('<style>div.row-widget.stRadio > div{flex-direction:row;}</style>', unsafe_allow_html=True)

def welcome_message():
    st.title("Welcome to the Stocks Performance api, through the prism of the S&P 500 Index components.")
    st.title(" ")
    st.write("                           by Boris Li, 2021")

def unpack_year_quarter(year_quarter:int):
    year = str(year_quarter)[:4]
    quarter_ending_month_dict = dict(zip(range(1,5), 
                                        ['March', 'June', 'September', 'December']))
    quarter_ending_month = quarter_ending_month_dict[int(year_quarter[-1])]
    return f'{quarter_ending_month} {year}'

def assemble_year_quarter(quarterly_dict:dict()):
    year = str(int(quarterly_dict['year']))
    quarter_ending_month_dict = dict(zip(range(1,5), 
                                        ['March', 'June', 'September', 'December']))
    quarter_ending_month = quarter_ending_month_dict[int(quarterly_dict['quarter'])]

    return f'{quarter_ending_month} {year}'

def get_financial_item_unit(financial_item):
    usd_financial_items = ['revenue', 'net_income', 'earnings_per_share', 'closing_price']
    financial_item_unit_dict = {usd_item: 'USD' for usd_item in usd_financial_items}
    financial_item_unit_dict['profit_margin'] = 'percentage'
    financial_item_unit_dict['price_earnings_ratio'] = ''
    return financial_item_unit_dict[financial_item]

def provide_financial_indicator_choice_menu():
    st.sidebar.header("Please select a financial indicator from")
    quarterly_report_item_selected = st.sidebar.multiselect('either time-period indicators:',
                                                        ['revenue', 'net_income', 'earnings_per_share', 'profit_margin'])
    point_in_time_item_selected = st.sidebar.multiselect('or point-in-time indicators:', ['closing_price', 'price_earnings_ratio'])
    if st.sidebar.button("Show historical financial performance:"):
        try:
            if quarterly_report_item_selected or point_in_time_item_selected:
                st.write(quarterly_report_item_selected)
                st.write(point_in_time_item_selected)
        except:
            print("Please select only as many indicators as of interest.")

    # quarterly_report_item_selected, point_in_time_item_selected = streamlit_sidebar_choices() # TBD streamlit_radio_button_choices()
    

def streamlit_sidebar_choices():
    st.sidebar.header("Please select a financial indicator from")
    quarterly_report_item_selected = st.sidebar.multiselect('either time-period indicators:',
                                                        ['revenue', 'net_income', 'earnings_per_share', 'profit_margin'])
    point_in_time_item_selected = st.sidebar.multiselect('or point-in-time indicators:', ['closing_price', 'price_earnings_ratio'])
    if st.sidebar.button("Show historical financial performance:"):
        st.write(quarterly_report_item_selected)
        st.write(point_in_time_item_selected)
        return quarterly_report_item_selected, point_in_time_item_selected

# to be replaced with st.button
@st.cache(suppress_st_warning=True)
def streamlit_radio_button_choices():
    time_period_financial_items = [''] + [underscored_to_spaced_words_dict(item) for item 
                                            in ['revenue', 'net_income', 'earnings_per_share', 'profit_margin']]
    quarterly_report_item_selected = st.radio('either time-period financial items:', time_period_financial_items, key= 'quarterly_report_key')
    point_in_time_item_selected = st.radio('or point-in-time info:', [''] + [underscored_to_spaced_words_dict(item)
                                                                                for item in ['closing_price', 'price_earnings_ratio']],
                                                                                key= 'point_in_time_key')
    return quarterly_report_item_selected, point_in_time_item_selected
    # wait for user's selection
    # while bool(quarterly_report_item_selected) & bool(point_in_time_item_selected) == False:
    
    # while or for loop
    # generator

    #if bool(quarterly_report_item_selected) & bool(point_in_time_item_selected) == True:
    #    print("Please select only one indicator from the two categories above.")
    # bool(quarterly_report_item_selected) or bool(point_in_time_item_selected):

        

def underscored_to_spaced_words_dict(underscored_words_financial_item, 
                                     underscored_words_financial_items 
                                        = ['revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'closing_price', 'price_earnings_ratio']):
    spaced_words_financial_items = underscored_to_spaced(
                                                    underscored_words_financial_items)
    conversion_dict = dict(zip(underscored_words_financial_items,
                                spaced_words_financial_items))
    return conversion_dict[underscored_words_financial_item]

def spaced_to_underscored_words_dict(spaced_words_financial_item,
                                     spaced_words_financial_items
                                        = ['Revenue', 'Net Income', 'Earnings Per Share', 'Profit Margin', 'Closing Price', 'Price Earnings Ratio']):
    underscored_words_financial_items = spaced_to_underscored(spaced_words_financial_items)
    conversion_dict = dict(zip(spaced_words_financial_items,
                                underscored_words_financial_items))
    return conversion_dict[spaced_words_financial_item]

def underscored_to_spaced(underscored_words_financial_items:list):
    transformed_financial_items_list = []
    for underscored_words in underscored_words_financial_items:
        if '_' not in underscored_words:
            transformed_financial_items_list.append(underscored_words.capitalize())
        else:
            spaced_words = ' '.join([word.capitalize() 
                                            for word in underscored_words.split('_')])
            transformed_financial_items_list.append(spaced_words)
    return transformed_financial_items_list      

def spaced_to_underscored(spaced_words_financial_items:list):
    underscored_words_list = []
    for words in spaced_words_financial_items:
        underscored_words = '_'.join(words.lower().split(' '))
        underscored_words_list.append(underscored_words)
    return underscored_words_list
