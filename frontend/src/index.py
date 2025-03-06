import streamlit as st
import pandas as pd
import plotly.express as px
from api.client import APIClient

def main():
    st.title("S&P 500 Economic Analysis Platform")
    st.markdown("""
    <div style='text-align: center; padding: 1rem;'>
        <h3>Advanced Financial Analytics Pipeline</h3>
        <p style='color: #666; font-size: 1.1em; margin-top: 0.5rem;'>
            Enterprise-grade financial insights powered by sophisticated data engineering:<br>
            Automated quarterly SEC filings processing • Cloud-native ETL pipeline<br>
            Distributed data persistence • Advanced analytics • Interactive visualization
        </p>
        <p style='color: #666; font-size: 1.1em; margin-top: 0.5rem;'>
            By Boris Li | Data Engineering & Financial Analytics
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize API client
    client = APIClient()
    
    # Sidebar for controls
    st.sidebar.header("Filters")
    sectors = client.get_sectors()
    selected_sector = st.sidebar.selectbox("Select Sector", sectors)
    
    # Get sector metrics
    metrics = client.get_sector_metrics(selected_sector)
    
    # Display financial metrics
    st.header(f"{selected_sector} Sector Overview")
    col1, col2, col3 = st.columns(3)
    col1.metric("Average Revenue", f"${metrics['avg_revenue']}M")
    col2.metric("Average Profit Margin", f"{metrics['avg_profit_margin']}%")
    col3.metric("Total Market Cap", f"${metrics['total_market_cap']}B")
    
    # Historical performance chart
    st.header("Historical Performance")
    data = client.get_sector_performance(selected_sector)
    fig = px.line(data, x='date', y='value', title=f"{selected_sector} Performance")
    st.plotly_chart(fig)
    
    # Data source attribution and professional footer
    st.markdown("---")
    st.markdown("""
    <div style='margin-top: 3rem; text-align: center;'>
        <p style='color: #666;'>
            Data provided by <a href='https://financialmodelingprep.com/developer/docs/' target='_blank'>Financial Modeling Prep</a>
        </p>
        <p style='color: #666; font-size: 0.9em; margin-top: 1rem;'>
            Enterprise Financial Analytics Platform<br>
            Developed by Boris Li
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()

