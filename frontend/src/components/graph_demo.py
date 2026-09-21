"""
Graph Intelligence Showcase Component for Streamlit.
Demonstrates Neo4j GDS deal proximity scoring and federated LLM query routing offline-safely.
"""
import streamlit as st
import plotly.graph_objects as go

def render_graph_intelligence_tab():
    st.header("🕸️ Private Equity Graph Relationship Intelligence (`graph_intelligence`)")
    st.markdown(
        """
        This microservice demonstrates **graph data science (Neo4j GDS)**, multi-hop relationship traversal,
        and **federated LLM intent routing** for private equity investment screening and deal proximity scoring.
        """
    )
    
    st.markdown("---")
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("1. Deal Proximity Scoring")
        st.write("Select private equity fund portfolio anchor holdings:")
        selected_portfolio = st.multiselect(
            "Portfolio Holdings",
            options=["AAPL", "MSFT", "NVDA", "GOOGL", "AMZN"],
            default=["AAPL", "MSFT"],
            key="graph_portfolio_select"
        )
        
        max_hops = st.slider("Max Traversal Hops", min_value=1, max_value=3, value=2, key="graph_hops_slider")
        run_traversal = st.button("Run Graph Proximity Traversal", key="run_graph_btn", type="primary")

    # Fixture-backed candidate graph database
    all_candidates = [
        {"ticker": "TSMC", "name": "Taiwan Semiconductor", "proximity": 0.94, "path_type": "tier_1_supply_chain", "ridge_score": 8.7, "hops": 1},
        {"ticker": "AVGO", "name": "Broadcom Inc.", "proximity": 0.89, "path_type": "tier_1_supply_chain", "ridge_score": 8.4, "hops": 1},
        {"ticker": "CRWD", "name": "CrowdStrike Holdings", "proximity": 0.82, "path_type": "direct_co_investment", "ridge_score": 7.9, "hops": 2},
        {"ticker": "NOW", "name": "ServiceNow Inc.", "proximity": 0.78, "path_type": "board_interlock", "ridge_score": 7.5, "hops": 2},
        {"ticker": "SNOW", "name": "Snowflake Inc.", "proximity": 0.73, "path_type": "direct_co_investment", "ridge_score": 7.2, "hops": 2},
        {"ticker": "ASML", "name": "ASML Holding", "proximity": 0.69, "path_type": "tier_2_supply_chain", "ridge_score": 8.1, "hops": 3},
    ]

    filtered_candidates = [c for c in all_candidates if c["hops"] <= max_hops]

    with col2:
        st.subheader(f"Candidates Identified Within {max_hops} Hops ({len(filtered_candidates)} found)")
        
        # Display candidates in a Plotly bar chart
        fig = go.Figure()
        fig.add_trace(go.Bar(
            y=[f"{c['name']} ({c['ticker']})" for c in filtered_candidates],
            x=[c['proximity'] for c in filtered_candidates],
            orientation='h',
            name="Proximity Score",
            marker=dict(color="#4F46E5"),
            text=[f"Score: {c['proximity']} | {c['path_type']}" for c in filtered_candidates],
            textposition="auto"
        ))
        fig.update_layout(
            title=f"Graph Proximity Traversal from Portfolio ({', '.join(selected_portfolio)})",
            xaxis_title="Proximity Score (0.0 to 1.0)",
            yaxis=dict(autorange="reversed"),
            height=320,
            margin=dict(l=20, r=20, t=40, b=20)
        )
        st.plotly_chart(fig, use_container_width=True)

    # Candidate Detail Table
    st.subheader("Candidate Deal Scoring & Relationship Pathways")
    cols_display = []
    for c in filtered_candidates:
        cols_display.append({
            "Ticker": c["ticker"],
            "Company Name": c["name"],
            "Neo4j Proximity": f"{c['proximity']:.2f}",
            "Relationship Pathway": c["path_type"].replace("_", " ").title(),
            "RidgeCV Attractiveness (1-10)": f"{c['ridge_score']:.1f}",
            "Graph Distance": f"{c['hops']} Hop(s)"
        })
    st.table(cols_display)

    st.markdown("---")
    st.subheader("2. Federated LLM Query Routing Engine")
    st.write("Test multi-source intent routing across Neo4j GDS, PostgreSQL (Financial Statements), and FAISS (Transcripts):")
    
    sample_queries = [
        "Screen private equity targets with deal proximity > 0.8 and EV/EBITDA < 18",
        "Find semiconductor suppliers connected to Apple with declining gross margins",
        "Extract management sentiment on AI capex from latest earnings calls"
    ]
    selected_sample = st.selectbox("Sample Investment Queries", sample_queries, key="graph_query_select")
    custom_query = st.text_input("Or enter custom analyst query:", value=selected_sample, key="graph_custom_query")

    if "proximity" in custom_query.lower() or "targets" in custom_query.lower():
        routing_result = {
            "query": custom_query,
            "target_data_stores": ["Neo4j GDS (Relationship Graph)", "PostgreSQL (Financial Ratios)"],
            "intent": "MULTI_SOURCE_SCREENING",
            "extracted_filters": {"min_proximity": 0.8, "metric": "ev_to_ebitda", "threshold": 18.0},
            "routing_confidence": 0.96,
            "execution_status": "Governed Tool Invocation Success"
        }
    elif "sentiment" in custom_query.lower() or "transcript" in custom_query.lower():
        routing_result = {
            "query": custom_query,
            "target_data_stores": ["FAISS Vector Store (Transcripts)", "PostgreSQL (Fundamentals)"],
            "intent": "NLP_TRANSCRIPT_SEARCH",
            "extracted_filters": {"topic": "AI capex", "granularity": "executive_remarks"},
            "routing_confidence": 0.94,
            "execution_status": "Governed Tool Invocation Success"
        }
    else:
        routing_result = {
            "query": custom_query,
            "target_data_stores": ["Neo4j GDS", "PostgreSQL"],
            "intent": "SUPPLY_CHAIN_PROXIMITY",
            "extracted_filters": {"anchor_ticker": "AAPL", "supply_tier": 1},
            "routing_confidence": 0.91,
            "execution_status": "Governed Tool Invocation Success"
        }

    st.json(routing_result)
