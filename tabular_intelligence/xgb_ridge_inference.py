"""XGBoost and Ridge inference engine for tabular financial predictions.

Strict offline-safe path: when USE_MOCK_ANALYTICS=true, deterministic
fixture predictors emit validated InferencePrediction objects with no
live model binaries required.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import ClassVar, Literal

import numpy as np

from tabular_intelligence.contracts import (
    InferencePrediction,
    TabularFeatureVector,
    USE_MOCK_ANALYTICS,
)


class _Predictor:
    """Abstract base for inference predictors."""

    model_type: ClassVar[Literal["xgboost", "ridge"]]

    def __init__(self, model: object | None = None) -> None:
        self.model = model

    def predict(self, feature_vector: TabularFeatureVector) -> InferencePrediction:
        raise NotImplementedError


def _feature_matrix(feature_vector: TabularFeatureVector) -> np.ndarray:
    arrays = (
        feature_vector.revenue,
        feature_vector.eps,
        feature_vector.closing_price,
        feature_vector.historical_volatility,
    )
    if len({len(array) for array in arrays}) != 1:
        raise ValueError("all feature arrays must have the same length")
    return np.column_stack(
        [np.asarray(array, dtype=float) for array in arrays]
    )


class XGBoostPredictor(_Predictor):
    """XGBoost regression wrapper with offline-safe mock fallback."""

    model_type: ClassVar[Literal["xgboost"]] = "xgboost"

    def fit(self, feature_vector: TabularFeatureVector) -> "XGBoostPredictor":
        if USE_MOCK_ANALYTICS:
            raise RuntimeError("live XGBoost initialization is disabled by USE_MOCK_ANALYTICS=true")
        import xgboost

        if self.model is None:
            self.model = xgboost.XGBRegressor(
                n_estimators=10,
                random_state=42,
                verbosity=0,
            )
        matrix = _feature_matrix(feature_vector)
        target = np.asarray(feature_vector.historical_volatility, dtype=float)
        self.model.fit(matrix, target)
        return self

    def predict(self, feature_vector: TabularFeatureVector) -> InferencePrediction:
        if USE_MOCK_ANALYTICS:
            prediction = float(np.mean(feature_vector.historical_volatility)) + 0.01
            return InferencePrediction(
                prediction=round(prediction, 4),
                confidence=0.82,
                model_type="xgboost",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        if self.model is None:
            self.fit(feature_vector)
        prediction = float(np.asarray(self.model.predict(_feature_matrix(feature_vector)))[0])
        return InferencePrediction(
            prediction=round(prediction, 4),
            confidence=0.75,
            model_type="xgboost",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


class RidgePredictor(_Predictor):
    """Ridge regression wrapper with offline-safe mock fallback."""

    model_type: ClassVar[Literal["ridge"]] = "ridge"

    def fit(self, feature_vector: TabularFeatureVector) -> "RidgePredictor":
        if USE_MOCK_ANALYTICS:
            raise RuntimeError("live Ridge initialization is disabled by USE_MOCK_ANALYTICS=true")
        import sklearn.linear_model

        if self.model is None:
            self.model = sklearn.linear_model.Ridge(alpha=1.0)
        matrix = _feature_matrix(feature_vector)
        target = np.asarray(feature_vector.historical_volatility, dtype=float)
        self.model.fit(matrix, target)
        return self

    def predict(self, feature_vector: TabularFeatureVector) -> InferencePrediction:
        if USE_MOCK_ANALYTICS:
            prediction = float(np.mean(feature_vector.historical_volatility))
            return InferencePrediction(
                prediction=round(prediction, 4),
                confidence=0.82,
                model_type="ridge",
                timestamp=datetime.now(timezone.utc).isoformat(),
            )

        if self.model is None:
            self.fit(feature_vector)
        prediction = float(np.asarray(self.model.predict(_feature_matrix(feature_vector)))[0])
        return InferencePrediction(
            prediction=round(prediction, 4),
            confidence=0.70,
            model_type="ridge",
            timestamp=datetime.now(timezone.utc).isoformat(),
        )


def get_predictor(model_type: str) -> _Predictor:
    """Factory routing to the correct predictor instance."""
    routing: dict[str, _Predictor] = {
        "xgboost": XGBoostPredictor(),
        "ridge": RidgePredictor(),
    }
    if model_type not in routing:
        raise ValueError(f"unsupported model_type: {model_type}. Use 'xgboost' or 'ridge'.")
    return routing[model_type]
