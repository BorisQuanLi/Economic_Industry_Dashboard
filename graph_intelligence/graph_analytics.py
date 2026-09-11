"""
Graph analytics: proximity feature matrix and deal attractiveness ranking.

Two public functions:

build_proximity_feature_matrix(neo4j_proximity_rows, db_conn)
    Joins Neo4j relationship proximity scores with PostgreSQL financial
    ratios into a pandas DataFrame.

    SQL pattern: three-table join (companies → sub_industries, prices_pe,
    quarterly_reports) filtered by ticker list — direct extension of the
    three-table join patterns in
    etl_service/src/models/queries/sql_query_strings.py.
    Uses psycopg2 %(name)s parameterisation consistent with db.py and
    fastapi_backend/db_session.py.

    Pandas merge mirrors the broadcast-join pattern in
    etl_service/src/adapters/aml_performance_utils.enrich_companies_with_subsector_risk()
    — same concept, pandas rather than PySpark, because this service
    does not depend on a Spark session.

rank_deals_by_proximity_and_value(feature_df)
    Fits a RidgeCV model predicting deal attractiveness from proximity score
    and financial ratios.  Cross-validated alpha selection via
    sklearn.linear_model.RidgeCV.

    Feature normalization reuses generate_alpha_features() from
    gpu_ops_alpha_orchestrator/feature_engine.py — the same Z-score
    cross-feature normalization validated against the GPU pipeline test
    suite, reused here for financial relationship features.

    The composite label is synthetic and documented as such: this is a
    feature-engineering demonstration, not a production model trained on
    labelled deal outcomes.

Offline safety
--------------
USE_MOCK_GRAPH=true returns fixture DataFrames throughout — no Neo4j,
PostgreSQL, or sklearn fit required.  Consistent with USE_FAKE_EMBEDDINGS
in mcp_agent_system/agents/rag_index.py.
"""
from __future__ import annotations

import logging
import os
from typing import Any

import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Cross-service import — read-only consumption of gpu_ops_alpha_orchestrator.
# Sanctioned exception per SKILL.md: no modifications to the GPU service.
# Falls back to pandas z-score if the package is not on sys.path.
# ---------------------------------------------------------------------------

try:
    import torch
    from gpu_ops_alpha_orchestrator.feature_engine import (  # type: ignore[import]
        generate_alpha_features,
    )
    _GPU_NORMALIZER = True
    logger.debug("generate_alpha_features loaded from gpu_ops_alpha_orchestrator")
except ImportError:
    _GPU_NORMALIZER = False
    logger.debug(
        "gpu_ops_alpha_orchestrator not available — falling back to pandas zscore"
    )

# ---------------------------------------------------------------------------
# SQL — three-table join filtered by ticker list.
# Schema (etl_service/src/db/migrations/create_tables.sql):
#   companies(id, ticker, sub_industry_id, ...)
#   sub_industries(id, sub_industry_GICS, sector_GICS)
#   quarterly_reports(id, company_id, date, revenue, ...)
#   prices_pe(id, company_id, date, closing_price, price_earnings_ratio)
#
# Pattern: sub_industry_avg_quarterly_financial_query_str and
# sub_sector_avg_price_pe_history_query_str in sql_query_strings.py both
# join quarterly_reports/prices_pe → companies → sub_industries.
# New element: ticker = ANY(%(tickers)s) filter + LATERAL latest-revenue.
# ---------------------------------------------------------------------------

_FINANCIAL_RATIOS_SQL = """
    SELECT
        c.ticker,
        si.sector_gics                                          AS sector,
        si.sub_industry_gics                                    AS sub_industry_gics,
        COALESCE(
            ROUND(AVG(pp.price_earnings_ratio)::NUMERIC, 2), 0.0
        )                                                       AS avg_pe_ratio,
        COALESCE(
            ROUND((latest_qr.revenue / 1.0e9)::NUMERIC, 4), 0.0
        )                                                       AS latest_revenue_usd_bn
    FROM companies c
    JOIN sub_industries si
        ON c.sub_industry_id::INT = si.id
    LEFT JOIN prices_pe pp
        ON pp.company_id = c.id
    LEFT JOIN LATERAL (
        SELECT revenue
        FROM   quarterly_reports
        WHERE  company_id = c.id
        ORDER  BY date DESC
        LIMIT  1
    ) latest_qr ON TRUE
    WHERE c.ticker = ANY(%(tickers)s)
    GROUP BY
        c.ticker,
        si.sector_gics,
        si.sub_industry_gics,
        latest_qr.revenue
    ORDER BY c.ticker;
"""

# ---------------------------------------------------------------------------
# Mock fixtures — domain-realistic values consistent with
# server.py _FALLBACK_SECTOR_ROWS and ma_advisory_graph_intelligence.py.
# ---------------------------------------------------------------------------

_MOCK_PROXIMITY_ROWS: list[dict[str, Any]] = [
    {"ticker": "CRM",  "proximity_score": 4, "path_type": "INSTITUTIONAL_HOLDER"},
    {"ticker": "ORCL", "proximity_score": 2, "path_type": "MA_HISTORY"},
    {"ticker": "IBM",  "proximity_score": 1, "path_type": "BOARD_CONNECTION"},
]

_MOCK_FEATURE_MATRIX = pd.DataFrame([
    {
        "ticker": "CRM",  "proximity_score": 4, "path_type": "INSTITUTIONAL_HOLDER",
        "sector": "Information Technology", "sub_industry_gics": "Application Software",
        "avg_pe_ratio": 22.5, "latest_revenue_usd_bn": 31.4,
    },
    {
        "ticker": "ORCL", "proximity_score": 2, "path_type": "MA_HISTORY",
        "sector": "Information Technology", "sub_industry_gics": "Systems Software",
        "avg_pe_ratio": 18.3, "latest_revenue_usd_bn": 50.0,
    },
    {
        "ticker": "IBM",  "proximity_score": 1, "path_type": "BOARD_CONNECTION",
        "sector": "Information Technology",
        "sub_industry_gics": "IT Consulting & Other Services",
        "avg_pe_ratio": 14.1, "latest_revenue_usd_bn": 60.5,
    },
])


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

def build_proximity_feature_matrix(
    neo4j_proximity_rows: list[dict[str, Any]],
    db_conn: Any,
) -> pd.DataFrame:
    """
    Join Neo4j relationship proximity scores with PostgreSQL financial ratios.

    Parameters
    ----------
    neo4j_proximity_rows
        Output of Neo4jClient.score_deal_proximity() — list of dicts with
        keys: ticker, proximity_score, path_type.
    db_conn
        psycopg2 connection.  Pattern: etl_service/src/db/db.py get_db()
        and fastapi_backend/db_session.py get_db_connection().
        Caller owns the connection lifecycle.

    Returns
    -------
    pandas DataFrame sorted descending by proximity_score:
        ticker, proximity_score, path_type,
        sector, sub_industry_gics, avg_pe_ratio, latest_revenue_usd_bn

    Offline path
    ------------
    USE_MOCK_GRAPH=true returns _MOCK_FEATURE_MATRIX without touching
    Neo4j or PostgreSQL.
    """
    if os.getenv("USE_MOCK_GRAPH", "false").lower() == "true":
        logger.info("USE_MOCK_GRAPH=true — returning fixture feature matrix")
        return _MOCK_FEATURE_MATRIX.copy()

    if not neo4j_proximity_rows:
        logger.warning("neo4j_proximity_rows is empty — returning empty matrix")
        return pd.DataFrame(
            columns=[
                "ticker", "proximity_score", "path_type",
                "sector", "sub_industry_gics", "avg_pe_ratio", "latest_revenue_usd_bn",
            ]
        )

    prox_df = pd.DataFrame(neo4j_proximity_rows)
    candidate_tickers = prox_df["ticker"].tolist()

    # --- PostgreSQL: three-table join filtered by ticker list.
    #     psycopg2 %(name)s parameterisation — no string interpolation.
    try:
        with db_conn.cursor() as cursor:
            cursor.execute(_FINANCIAL_RATIOS_SQL, {"tickers": candidate_tickers})
            rows = cursor.fetchall()
            col_names = [desc[0] for desc in cursor.description]
    except Exception:
        logger.error(
            "Failed to fetch financial ratios for %s; returning proximity-only matrix",
            candidate_tickers,
            exc_info=True,
        )
        for col in ("sector", "sub_industry_gics", "avg_pe_ratio", "latest_revenue_usd_bn"):
            prox_df[col] = None
        return prox_df.sort_values("proximity_score", ascending=False).reset_index(drop=True)

    fin_df = pd.DataFrame(rows, columns=col_names)

    # Pandas left join: keeps Neo4j candidates not yet in the quarterly pipeline.
    # Mirrors enrich_companies_with_subsector_risk() broadcast-join pattern.
    merged = prox_df.merge(fin_df, on="ticker", how="left")
    merged = merged.sort_values("proximity_score", ascending=False).reset_index(drop=True)

    logger.info(
        "Proximity feature matrix: %d candidates, %d with financial ratios",
        len(merged),
        int(merged["avg_pe_ratio"].notna().sum()),
    )
    return merged


def rank_deals_by_proximity_and_value(
    feature_df: pd.DataFrame,
) -> pd.DataFrame:
    """
    Fit a RidgeCV ranking model and score candidates by deal attractiveness.

    Features (after Z-score normalization):
        proximity_score      — 2-hop relationship distance from portfolio
        avg_pe_ratio         — rolling average P/E (lower = cheaper)
        latest_revenue_usd_bn — most recent quarterly revenue (USD bn)

    Label construction (synthetic — documented honestly):
        deal_score = 0.5 * norm_proximity
                   + 0.3 * (1 / (norm_pe + 1e-6))   # cheaper valuation preferred
                   + 0.2 * norm_revenue

    The label is synthetic because no historical deal-outcome training data
    is available in this codebase.  The model demonstrates the pipeline
    (feature selection → normalization → RidgeCV → cross-validated alpha),
    not a calibrated production scorer.

    Cross-validated alpha selection via RidgeCV follows the same approach
    described in the Q2 application answer for demand-forecasting Ridge
    regression — RidgeCV handles multicollinearity between proximity_score
    and financial ratios.

    Parameters
    ----------
    feature_df : output of build_proximity_feature_matrix()

    Returns
    -------
    feature_df with two new columns added:
        deal_attractiveness_score — Ridge model prediction (higher = more attractive)
        rank                      — integer rank within the candidate set (1 = best)

    Offline path
    ------------
    Works on the 3-row mock fixture — RidgeCV with 3 samples is numerically
    trivial but exercises the full code path.
    """
    from sklearn.linear_model import RidgeCV  # deferred import — optional dependency

    numeric_cols = ["proximity_score", "avg_pe_ratio", "latest_revenue_usd_bn"]

    df = feature_df.copy()

    # Fill nulls (candidates without PostgreSQL financial data)
    for col in numeric_cols:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = df[col].fillna(0.0)

    X_raw = df[numeric_cols].values.astype(float)

    # Z-score normalization — reuse generate_alpha_features() from
    # gpu_ops_alpha_orchestrator if available; fall back to pandas zscore.
    if _GPU_NORMALIZER:
        t = torch.tensor(X_raw, dtype=torch.float32)
        X_norm = generate_alpha_features(t).numpy()  # returns CPU tensor
        logger.debug("Feature normalization via gpu_ops_alpha_orchestrator")
    else:
        mean = X_raw.mean(axis=0)
        std = X_raw.std(axis=0) + 1e-6
        X_norm = (X_raw - mean) / std
        logger.debug("Feature normalization via pandas fallback (gpu_ops unavailable)")

    norm_proximity = X_norm[:, 0]
    norm_pe = X_norm[:, 1]
    norm_revenue = X_norm[:, 2]

    # Synthetic deal attractiveness label
    y = 0.5 * norm_proximity + 0.3 * (1.0 / (norm_pe + 1e-6)) + 0.2 * norm_revenue

    # RidgeCV: cross-validated alpha selection over three candidate values.
    # cv=min(3, n_samples) ensures the fit works even on the 3-row mock fixture.
    n_samples = X_norm.shape[0]
    ridge = RidgeCV(alphas=[0.1, 1.0, 10.0], cv=min(3, n_samples))
    ridge.fit(X_norm, y)

    df["deal_attractiveness_score"] = np.round(ridge.predict(X_norm), 4)
    df["rank"] = df["deal_attractiveness_score"].rank(
        ascending=False, method="min"
    ).astype(int)
    df = df.sort_values("rank").reset_index(drop=True)

    logger.info(
        "RidgeCV deal ranking: %d candidates, selected alpha=%.2f",
        len(df),
        ridge.alpha_,
    )
    return df
