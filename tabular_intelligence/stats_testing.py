"""Statistical hypothesis testing engine for tabular financial data.

Offline-safe: when USE_MOCK_ANALYTICS=true, operates on fixture arrays
without requiring external statistical binaries or network access. The
live path uses SciPy's two-sample t-test and one-way ANOVA implementations.
"""

from __future__ import annotations

import statistics
from collections.abc import Sequence
from math import sqrt

from tabular_intelligence.contracts import USE_MOCK_ANALYTICS


class HypothesisTest:
    """Two-sample t-test and one-way ANOVA for cross-cycle feature shifts."""

    def __init__(self, group_a: Sequence[float], group_b: Sequence[float]) -> None:
        self.group_a = list(group_a)
        self.group_b = list(group_b)
        self._validate_group(self.group_a, "group_a")
        self._validate_group(self.group_b, "group_b")

    @staticmethod
    def _validate_group(values: Sequence[float], name: str) -> None:
        if len(values) < 2:
            raise ValueError(f"{name} must contain at least two observations")

    @classmethod
    def _mock_p_value(cls, group_a: Sequence[float], group_b: Sequence[float]) -> float:
        """Return a deterministic pseudo p-value bounded to [0, 1].

        This fixture is intentionally not a substitute for a production
        p-value; it is used only to exercise offline contracts and routing.
        """
        mean_a = statistics.mean(group_a)
        mean_b = statistics.mean(group_b)
        difference = abs(mean_a - mean_b)
        variance_scale = statistics.variance(group_a) + statistics.variance(group_b)
        if difference <= 1e-12:
            return 1.0
        if variance_scale <= 1e-12:
            return 0.0

        effect = difference / sqrt(variance_scale)
        return 1.0 / (1.0 + effect)

    def p_value(self) -> float:
        if USE_MOCK_ANALYTICS:
            return self._mock_p_value(self.group_a, self.group_b)

        from scipy.stats import ttest_ind

        result = ttest_ind(self.group_a, self.group_b, equal_var=False)
        return float(result.pvalue)

    def anova(self, groups: Sequence[Sequence[float]]) -> float:
        """Calculate a one-way ANOVA p-value across two or more cycles."""
        if len(groups) < 2:
            raise ValueError("ANOVA requires at least two groups")
        for index, group in enumerate(groups):
            self._validate_group(group, f"groups[{index}]")

        if USE_MOCK_ANALYTICS:
            flattened = [value for group in groups for value in group]
            overall_mean = statistics.mean(flattened)
            between = sum(len(group) * (statistics.mean(group) - overall_mean) ** 2 for group in groups)
            within = sum(
                sum((value - statistics.mean(group)) ** 2 for value in group)
                for group in groups
            )
            if between <= 1e-12:
                return 1.0
            if within <= 1e-12:
                return 0.0
            return 1.0 / (1.0 + between / within)

        from scipy.stats import f_oneway

        result = f_oneway(*groups)
        return float(result.pvalue)

    def is_significant(self, alpha: float = 0.05) -> bool:
        if not 0.0 < alpha < 1.0:
            raise ValueError("alpha must be between 0 and 1")
        return self.p_value() <= alpha
