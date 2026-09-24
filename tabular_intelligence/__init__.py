"""tabular_intelligence — Tabular ML and Statistics microservice.

Provides XGBoost/Ridge inference, hypothesis testing, and contract
validation for financial feature vectors.
"""

from tabular_intelligence.contracts import InferencePrediction, TabularFeatureVector

__all__ = ["InferencePrediction", "TabularFeatureVector"]
