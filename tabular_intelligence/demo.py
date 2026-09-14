"""Interactive offline demo for tabular intelligence."""

from __future__ import annotations

import sys
from pathlib import Path

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tabular_intelligence.contracts import TabularFeatureVector, USE_MOCK_ANALYTICS
from tabular_intelligence.stats_testing import HypothesisTest
from tabular_intelligence.xgb_ridge_inference import get_predictor


DEMO_VECTORS = [
    TabularFeatureVector(
        ticker="AAPL",
        revenue=[1.0, 1.1, 1.2],
        eps=[0.5, 0.55, 0.6],
        closing_price=[150.0, 151.0, 152.0],
        historical_volatility=[0.20, 0.22, 0.21],
    ),
    TabularFeatureVector(
        ticker="MSFT",
        revenue=[2.0, 2.1, 2.2],
        eps=[0.8, 0.84, 0.88],
        closing_price=[400.0, 402.0, 404.0],
        historical_volatility=[0.18, 0.20, 0.19],
    ),
    TabularFeatureVector(
        ticker="NVDA",
        revenue=[3.0, 3.2, 3.4],
        eps=[1.0, 1.1, 1.2],
        closing_price=[800.0, 810.0, 820.0],
        historical_volatility=[0.35, 0.38, 0.36],
    ),
]


def run_pipeline(model_type: str = "xgboost") -> tuple[float, float, list]:
    """Run cross-cycle testing and emit validated predictions."""
    eps_cycles = [vector.eps for vector in DEMO_VECTORS]
    comparison = HypothesisTest(eps_cycles[0], eps_cycles[1])
    anova_p_value = comparison.anova(eps_cycles)
    predictor = get_predictor(model_type)
    predictions = [predictor.predict(vector) for vector in DEMO_VECTORS]
    return comparison.p_value(), anova_p_value, predictions


def render_result(model_type: str, p_value: float, anova_p_value: float, predictions: list) -> None:
    print(f"\nTabular Intelligence Demo — mode: {'offline mock' if USE_MOCK_ANALYTICS else 'live'}")
    print(f"Cross-cycle EPS two-sample p-value: {p_value:.4f}")
    print(f"Cross-cycle EPS ANOVA p-value: {anova_p_value:.4f}")
    print(f"Predictor: {model_type}")
    for prediction in predictions:
        print(
            f"  {prediction.model_type:<9} prediction={prediction.prediction:.4f} "
            f"confidence={prediction.confidence:.2f} timestamp={prediction.timestamp}"
        )


def interactive_loop() -> None:
    """Run the demo repeatedly while stdin is interactive."""
    while True:
        choice = input("Choose predictor [xgboost/ridge/q]: ").strip().lower()
        if choice in {"q", "quit", "exit"}:
            print("Demo complete.")
            return
        if choice not in {"xgboost", "ridge"}:
            print("Invalid choice; enter xgboost, ridge, or q.")
            continue
        render_result(*run_pipeline(choice))


def main() -> None:
    if len(sys.argv) > 1:
        model_type = sys.argv[1]
        p_value, anova_p_value, predictions = run_pipeline(model_type)
        render_result(model_type, p_value, anova_p_value, predictions)
        return
    if sys.stdin.isatty():
        interactive_loop()
        return
    p_value, anova_p_value, predictions = run_pipeline("xgboost")
    render_result("xgboost", p_value, anova_p_value, predictions)


if __name__ == "__main__":
    main()
