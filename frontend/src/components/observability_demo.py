"""
Observability Showcase Component for Streamlit.
Demonstrates Pydantic telemetry tracing, evaluation scorecards, and Policy-as-Code governance.
"""
import streamlit as st

def render_observability_tab():
    st.header("🛡️ Cross-Service Telemetry & AI Evaluation (`observability_service`)")
    st.markdown(
        """
        This microservice demonstrates **cross-service telemetry tracing**, **deterministic evaluation scorecards**,
        and **Policy-as-Code governance** across the multi-service FSI architecture.
        """
    )
    
    st.markdown("---")
    st.subheader("1. End-to-End Workflow Telemetry Tracing (`TracePayload`)")
    st.write("Inspect structured trace contracts capturing token consumption, latency breakdown, and execution pathways:")
    
    trace_choice = st.selectbox(
        "Select Active Workflow Trace",
        [
            "tr-graph-screening-001 (PE Deal Proximity Traversal)",
            "tr-tabular-inference-002 (XGBoost Volatility Forecasting)",
            "tr-nlp-transcript-003 (Earnings Call Sentiment Extraction)"
        ],
        key="obs_trace_select"
    )

    traces = {
        "tr-graph-screening-001": {
            "trace_id": "tr-graph-screening-001",
            "service_name": "graph_intelligence",
            "workflow_path": ["intent_router", "neo4j_traversal", "ridgecv_ranking", "eval_scorecard"],
            "prompt_token_count": 284,
            "completion_token_count": 68,
            "tool_invocation_latency_ms": {"intent_router": 12.4, "neo4j_traversal": 41.2, "ridge_ranking": 2.1},
            "runtime_errors": None,
            "status": "COMPLETED_OK"
        },
        "tr-tabular-inference-002": {
            "trace_id": "tr-tabular-inference-002",
            "service_name": "tabular_intelligence",
            "workflow_path": ["schema_validation", "hypothesis_testing", "xgboost_infer"],
            "prompt_token_count": 0,
            "completion_token_count": 0,
            "tool_invocation_latency_ms": {"schema_validation": 0.3, "welch_t_test": 0.4, "xgb_infer": 1.4},
            "runtime_errors": None,
            "status": "COMPLETED_OK"
        },
        "tr-nlp-transcript-003": {
            "trace_id": "tr-nlp-transcript-003",
            "service_name": "etl_service + fastapi_backend",
            "workflow_path": ["transcript_sectioner", "rag_retrieval", "llm_extraction", "judge_eval"],
            "prompt_token_count": 1420,
            "completion_token_count": 185,
            "tool_invocation_latency_ms": {"faiss_query": 8.5, "llm_extract": 420.0, "judge_scorecard": 190.0},
            "runtime_errors": None,
            "status": "COMPLETED_OK"
        }
    }

    selected_key = trace_choice.split(" ")[0]
    trace = traces[selected_key]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Originating Service", trace["service_name"])
    c2.metric("Prompt Tokens", trace["prompt_token_count"])
    c3.metric("Completion Tokens", trace["completion_token_count"])
    total_lat = sum(trace["tool_invocation_latency_ms"].values())
    c4.metric("Total Tool Latency", f"{total_lat:.1f} ms")

    st.json(trace)

    st.markdown("---")
    st.subheader("2. Deterministic Evaluation Scorecards (`EvalScorecard`)")
    st.write("Deterministic quality metrics and LLM-as-a-judge scorecards with strict boundary enforcement `[0.0, 1.0]`:")

    eval_scorecards = [
        {"eval_id": "ev-01", "target_trace": "tr-graph-screening-001", "metric": "routing_accuracy", "score": 0.96, "evaluator": "deterministic_ground_truth"},
        {"eval_id": "ev-02", "target_trace": "tr-graph-screening-001", "metric": "proximity_calibration", "score": 0.91, "evaluator": "ridge_cross_validation"},
        {"eval_id": "ev-03", "target_trace": "tr-nlp-transcript-003", "metric": "extraction_fidelity", "score": 0.94, "evaluator": "llm_as_a_judge (Claude 3.5 Sonnet)"},
        {"eval_id": "ev-04", "target_trace": "tr-nlp-transcript-003", "metric": "hallucination_penalty", "score": 0.02, "evaluator": "citation_grounding_audit"},
    ]

    st.table(eval_scorecards)

    st.markdown("---")
    st.subheader("3. Policy-as-Code Governance Matrix")
    st.write("Live status of repository-wide human gates, session registries, and machine-readable constraints:")

    gov_status = [
        {"Artifact": "CLAUDE.md", "Scope": "Repository Root", "Function": "Master Architecture & Global AI Session Registry", "Status": "Active & Synchronized"},
        {"Artifact": "SKILL.md", "Scope": "Per-Microservice", "Function": "Machine-Readable Behavioral Constraints", "Status": "Enforced (Zero-Drift)"},
        {"Artifact": "AI_AUGMENTED_SDLC.md", "Scope": "Per-Microservice", "Function": "Human-in-the-Loop Review Gates", "Status": "Enforced"},
        {"Artifact": "AGENT_LOGS.md", "Scope": "Per-Microservice", "Function": "Cryptographic Session Decision Logs", "Status": "Audited & Logged"},
    ]
    st.table(gov_status)
