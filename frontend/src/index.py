import streamlit as st
st.set_page_config(page_title="Economic & Financial Intelligence Platform", layout="wide")
from datetime import datetime
from plot_sub_sector_financial_performance import plot_sub_sectors_performance
from plot_sector_financial_performance import plot_sector_level_performance
from plot_company_performance import plot_company_level_performance

from components.graph_demo import render_graph_intelligence_tab
from components.tabular_demo import render_tabular_intelligence_tab
from components.observability_demo import render_observability_tab

st.title("Economic & Financial Intelligence Platform — Multi-Service FSI Portfolio")
st.write(f"Architected & Maintained by Boris Li | {datetime.now().year} | S&P 500 Fundamentals & AI Engineering Services")

tab_macro, tab_graph, tab_tabular, tab_obs = st.tabs([
    "📈 S&P 500 Macro Fundamentals",
    "🕸️ PE Graph Relationship Intelligence",
    "📊 Tabular ML & Hypothesis Testing",
    "🛡️ Cross-Service Observability & Evals"
])

with tab_macro:
    financial_indicator_selected = plot_sector_level_performance()
    sub_sector_name, sub_sector_financial_indicator = plot_sub_sectors_performance(financial_indicator_selected)
    plot_company_level_performance(sub_sector_name, sub_sector_financial_indicator)

    st.markdown("---")
    st.caption("Data source: Financial Modeling Prep (FMP) API & SEC filings tier (offline fallback active): https://financialmodelingprep.com/developer/docs/")

with tab_graph:
    render_graph_intelligence_tab()

with tab_tabular:
    render_tabular_intelligence_tab()

with tab_obs:
    render_observability_tab()
