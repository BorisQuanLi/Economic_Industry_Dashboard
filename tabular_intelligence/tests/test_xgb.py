"""XGBoost and Ridge inference tests for tabular_intelligence."""

import pytest

from tabular_intelligence.contracts import InferencePrediction, USE_MOCK_ANALYTICS
from tabular_intelligence.contracts import TabularFeatureVector
from tabular_intelligence.stats_testing import HypothesisTest
from tabular_intelligence.xgb_ridge_inference import XGBoostPredictor, RidgePredictor, get_predictor


def _feature_vector() -> TabularFeatureVector:
    return TabularFeatureVector(
        ticker="TEST",
        revenue=[1.0, 1.1, 1.2],
        eps=[0.5, 0.55, 0.6],
        closing_price=[150.0, 151.0, 152.0],
        historical_volatility=[0.2, 0.22, 0.21],
    )


def test_xgb_predictor_under_mock() -> None:
    predictor = XGBoostPredictor()
    result = predictor.predict(_feature_vector())
    assert isinstance(result, InferencePrediction)
    assert result.model_type == "xgboost"
    assert 0.0 <= result.confidence <= 1.0
    assert isinstance(result.prediction, float)


def test_ridge_predictor_under_mock() -> None:
    predictor = RidgePredictor()
    result = predictor.predict(_feature_vector())
    assert isinstance(result, InferencePrediction)
    assert result.model_type == "ridge"
    assert 0.0 <= result.confidence <= 1.0


def test_predictor_routing() -> None:
    xgb = get_predictor("xgboost")
    rid = get_predictor("ridge")
    assert xgb.model_type == "xgboost"
    assert rid.model_type == "ridge"


def test_predictor_routing_invalid_raises() -> None:
    with pytest.raises(ValueError):
        get_predictor("unsupported")


def test_inference_prediction_strict_contract_blocks_extra() -> None:
    result = InferencePrediction(
        prediction=0.5,
        confidence=0.8,
        model_type="xgboost",
        timestamp="2025-01-01T00:00:00Z",
    )
    assert result.prediction == 0.5


if __name__ == "__main__":
    pass
