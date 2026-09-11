"""
graph_intelligence — Financial relationship intelligence microservice.

Provides graph-based relationship analysis for investment deal workflows:

  Deal sourcing     — proximity scoring via M&A history and institutional
                      holder networks; surfaces warm introduction paths
                      to target companies.

  Compliance        — multi-hop conflict-of-interest path detection across
                      board memberships, employment history, and co-investment
                      relationships; returns auditable paths, not just flags.

  Portfolio risk    — contagion exposure via shared institutional holders;
                      identifies correlated stress scenarios before they
                      appear in financials.

Sub-modules
-----------
neo4j_client
    Async Neo4j driver wrapper.  Offline-safe: USE_MOCK_GRAPH=true returns
    domain-realistic fixture data without a live connection.

graph_builder
    Ingests public M&A transaction records and SEC 13F institutional holder
    disclosures into Neo4j relationship edges.  Gated on
    RUN_GRAPH_INGESTION=true — never runs in CI or the demo path.

graph_analytics
    Joins Neo4j proximity scores with PostgreSQL financial ratios into a
    pandas DataFrame, then fits a RidgeCV ranking model predicting deal
    attractiveness.  Reuses generate_alpha_features() from
    gpu_ops_alpha_orchestrator for Z-score feature normalization.

federated_query_layer
    LLM-driven intent router over Neo4j + PostgreSQL + FAISS.  Data stays
    in source systems; the LLM routes analyst questions to the appropriate
    source(s) and merges results — the federated semantic layer pattern
    without RDF/SPARQL overhead.

company_search_tool
    LangChain tool-calling demo: natural-language financial company search
    via a financial screener cross-referenced with graph proximity scores.

Governance
----------
SKILL.md          — constraint manifest (offline contracts, scope isolation,
                    LLM injection contract, MCP tool boundary)
AGENT_LOGS.md     — session audit trail (Intent → Decision → Result)
AI_AUGMENTED_SDLC.md — methodology doc and sessions table

Branch: feat/graph-relationship-intelligence
"""
