import streamlit as st
from frontend_utilities import frontend_backend_string_format_conversion, get_indicators_in_frontend_format

def sector_level_first_round_choice_menu(user_choice=''):
    if not user_choice:
        instruction_default_selection = 'Other financial performance indicators can be selected from this pull-down menu:'
        indicators_in_backend_format = ['revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'closing_price', 'price_earnings_ratio']
        indicators_in_frontend_format = get_indicators_in_frontend_format(indicators_in_backend_format)
        first_round_choice = st.selectbox('', ([f'{instruction_default_selection}']
                                                + indicators_in_frontend_format
                                                + ['Go to the next section, Sub-Industries']), index=0)
        if first_round_choice == instruction_default_selection:
            # listening mode, wait for the user's section
            st.stop()
        elif first_round_choice == 'Go to the next section, Sub-Industries':
            user_choice = 'Continue to the Sub-Industry level.'
        else: user_choice = frontend_backend_string_format_conversion()[first_round_choice]
    return user_choice  

def sector_level_follow_up_choice_menu(key_value=0):
    follow_up_instruction = "Want to check out the history of another financial indicator?  Click the pull-down menu above again."
    choose_to_move_on = 'No, go to the next section, Sub Industries.'
    follow_up_choice = st.radio('', [f'{follow_up_instruction}', f'{choose_to_move_on}'], index=0, key=key_value)
    if follow_up_choice == follow_up_instruction:
        st.stop()
    else:
        return 'Continue to the Sub-Industry level.'

def sub_industry_first_round_choice_menu(sector_name, user_choice=''):
    if not user_choice:
        instruction_default_selection = 'Other financial performance indicators can be selected from this pull-down menu:'
        indicators_in_backend_format = ['revenue', 'net_income', 'earnings_per_share', 'profit_margin', 'closing_price', 'price_earnings_ratio']
        indicators_in_frontend_format = get_indicators_in_frontend_format(indicators_in_backend_format)
        first_round_choice = st.selectbox('', ([f'{instruction_default_selection}']
                                                + indicators_in_frontend_format
                                                + ['Go to the next section, Sub Industries']), index=0)
        if first_round_choice == instruction_default_selection:
            st.stop()
        else: user_choice = frontend_backend_string_format_conversion()[first_round_choice]
    return user_choice  
    
def sub_industry_follow_up_choice_menu(key_value=0):
    follow_up_instruction = "Want to check out the history of another financial indicator?  Click the pull-down menu above again."
    choose_to_move_on = 'No, go to the next section, Companies within a Sub Industry.'
    follow_up_choice = st.radio('', [f'{follow_up_instruction}', f'{choose_to_move_on}'], index=0, key=key_value)
    if follow_up_choice == follow_up_instruction:
        st.stop()
    else:
        return 'Inspect companies within a Sub-Industry.'