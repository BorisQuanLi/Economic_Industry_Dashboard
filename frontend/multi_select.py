import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

API_URL = "http://127.0.0.1:5000/test_st_multiselect/search"

def find_sector_company(**kwargs):
    breakpoint()
    response = requests.get(API_URL, params = kwargs)
    return response.json()


options = st.multiselect(
                    'Which sector and company are you interested in?',
                    ['Consumer Staples', 'Health Care', 'Information Technology'],
                    ['AAPL', 'PFE', 'JNJ', 'WMT'])
st.write('You selected:', options)

"""

options = st.multiselect(
'What are your favorite colors',
['Green', 'Yellow', 'Red', 'Blue'],
['Yellow', 'Red'])
st.write('You selected:', options)
"""