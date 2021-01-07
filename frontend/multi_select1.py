import streamlit as st
import requests
import plotly.graph_objects as go
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

API_URL = "http://127.0.0.1:5000/multiselect1/sector"

def multiselect1(sector):
    breakpoint()
    response = requests.get(API_URL, params = kwargs)
    return response.json()

sectors = st.multiselect(
                    'Which sector are you interested in?',
                    ['Consumer Staples', 'Health Care', 'Information Technology'],
                    ['Consumer Staples', 'Health Care', 'Information Technology'])
st.write('You selected:', sectors)