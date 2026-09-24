"""Tabular intelligence contracts and environment toggles.

Strict Pydantic v2 models with `extra="forbid"` to prevent silent
schema drift. All financial arrays are length-constrained to ensure
feature matrices remain rectangular during offline-safe inference.
"""

from __future__ import annotations

import os
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


# ---------------------------------------------------------------------------
# Environment toggles — preserve offline safety across CI and local runs.
# ---------------------------------------------------------------------------
USE_MOCK_ANALYTICS: bool = os.environ.get("USE_MOCK_ANALYTICS", "true").lower() == "true"


# ---------------------------------------------------------------------------
# Tabular feature vector — ingests financial fundamentals for ML inference.
# ---------------------------------------------------------------------------
class TabularFeatureVector(BaseModel):
    """Financial feature vector ingested by the tabular ML pipeline."""

    model_config = ConfigDict(extra="forbid")

    ticker: str = Field(..., min_length=1, description="Stock ticker symbol.")
    revenue: list[float] = Field(..., min_length=1, description="Trailing quarterly revenue series.")
    eps: list[float] = Field(..., min_length=1, description="Earnings-per-share series.")
    closing_price: list[float] = Field(..., min_length=1, description="Daily closing price series.")
    historical_volatility: list[float] = Field(..., min_length=1, description="Annualized volatility series.")

    @staticmethod
    def _all_same_length(*fields: list) -> bool:
        """Check that all provided fields have identical length."""
        lengths = [len(f) for f in fields if f is not None]
        return len(set(lengths)) <= 1

    @model_validator(mode="after")
    def _validate_feature_lengths(self) -> "TabularFeatureVector":
        if not self._all_same_length(self.revenue, self.eps, self.closing_price, self.historical_volatility):
            raise ValueError("all feature arrays must have the same length")
        return self

    @property
    def feature_length(self) -> int:
        """Return the canonical length shared by all feature arrays."""
        return len(self.revenue)


# ---------------------------------------------------------------------------
# Inference prediction — emitted by XGBoost or Ridge regression models.
# ---------------------------------------------------------------------------
class InferencePrediction(BaseModel):
    """Model prediction emitted by the tabular inference pipeline."""

    model_config = ConfigDict(extra="forbid", protected_namespaces=())

    prediction: float = Field(..., description="Predicted scalar (e.g. volatility delta).")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Model confidence score in [0, 1].")
    model_type: Literal["xgboost", "ridge"] = Field(..., description="Model architecture used.")
    timestamp: str = Field(..., description="ISO-8601 execution timestamp.")