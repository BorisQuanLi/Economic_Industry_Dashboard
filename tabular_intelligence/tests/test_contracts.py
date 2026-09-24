"""Contract validation tests for the tabular intelligence service."""

import pytest
from pydantic import ValidationError

from tabular_intelligence.contracts import TabularFeatureVector


def _valid_vector() -> dict[str, object]:
    return {
        "ticker": "AAPL",
        "revenue": [1.0, 1.1],
        "eps": [0.5, 0.6],
        "closing_price": [180.0, 182.0],
        "historical_volatility": [0.2, 0.25],
    }


def test_feature_vector_accepts_valid_financial_arrays() -> None:
    vector = TabularFeatureVector.model_validate(_valid_vector())

    assert vector.ticker == "AAPL"
    assert vector.historical_volatility == [0.2, 0.25]


def test_feature_vector_blocks_missing_required_fields() -> None:
    payload = _valid_vector()
    del payload["eps"]

    with pytest.raises(ValidationError):
        TabularFeatureVector.model_validate(payload)


def test_feature_vector_blocks_malformed_numeric_arrays() -> None:
    payload = _valid_vector()
    payload["historical_volatility"] = ["not-a-number"]

    with pytest.raises(ValidationError):
        TabularFeatureVector.model_validate(payload)


def test_feature_vector_blocks_mismatched_array_lengths() -> None:
    payload = _valid_vector()
    payload["closing_price"] = [180.0]

    with pytest.raises(ValidationError):
        TabularFeatureVector.model_validate(payload)


def test_feature_vector_forbids_unknown_fields() -> None:
    payload = _valid_vector()
    payload["unexpected"] = True

    with pytest.raises(ValidationError):
        TabularFeatureVector.model_validate(payload)
