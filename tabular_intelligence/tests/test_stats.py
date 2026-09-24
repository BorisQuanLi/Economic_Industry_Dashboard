"""Statistical testing unit tests for tabular_intelligence."""

import pytest

from tabular_intelligence.contracts import TabularFeatureVector
from tabular_intelligence.stats_testing import HypothesisTest, USE_MOCK_ANALYTICS


def _build_vector(values: list[float]) -> TabularFeatureVector:
    return TabularFeatureVector(
        ticker="TEST",
        revenue=values,
        eps=values,
        closing_price=values,
        historical_volatility=values,
    )


def test_p_value_returns_float() -> None:
    vt = HypothesisTest(group_a=[1.0, 2.0, 3.0], group_b=[4.0, 5.0, 6.0])
    p = vt.p_value()
    assert isinstance(p, float)
    assert 0.0 <= p <= 1.0


def test_significant_when_alpha_exceeds_p() -> None:
    vt = HypothesisTest(group_a=[0.1, 0.2], group_b=[0.9, 1.0])
    assert vt.is_significant(alpha=0.5) is True


def test_not_significant_when_alpha_below_p() -> None:
    vt = HypothesisTest(group_a=[1.0, 1.1], group_b=[1.05, 1.15])
    assert vt.is_significant(alpha=0.001) is False


def test_p_value_is_deterministic_under_mock() -> None:
    """Mock mode should always produce the same p-value for identical inputs."""
    vt1 = HypothesisTest(group_a=[1.0, 2.0], group_b=[3.0, 4.0])
    vt2 = HypothesisTest(group_a=[1.0, 2.0], group_b=[3.0, 4.0])
    assert vt1.p_value() == vt2.p_value()


def test_p_value_bounds() -> None:
    vt = HypothesisTest(group_a=[1.0, 1.0, 1.0], group_b=[1.0, 1.0, 1.0])
    assert vt.p_value() <= 1.0


def test_t_test_with_feature_vector() -> None:
    """End-to-end: feed real TabularFeatureVector arrays into HypothesisTest."""
    vf = _build_vector([1.0, 2.0, 3.0, 4.0])
    vt = HypothesisTest(group_a=vf.revenue, group_b=vf.closing_price)
    p = vt.p_value()
    assert isinstance(p, float)
    assert 0.0 <= p <= 1.0