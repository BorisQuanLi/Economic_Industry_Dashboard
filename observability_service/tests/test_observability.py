import pytest
from datetime import datetime
from pydantic import ValidationError
from observability_service.traces import TracePayload

def test_trace_payload_valid_instantiation():
    payload = TracePayload(
        trace_id="tr-001",
        service_name="graph_intelligence",
        workflow_path=["search", "rank"],
        prompt_token_count=150,
        completion_token_count=40,
        tool_invocation_latency={"reranker": 23.5},
        runtime_errors=None,
    )
    assert payload.trace_id == "tr-001"
    assert payload.prompt_token_count == 150

def test_trace_payload_rejects_extra_fields():
    with pytest.raises(ValidationError):
        TracePayload(
            trace_id="tr-002",
            service_name="tabular",
            workflow_path=["load"],
            prompt_token_count=100,
            completion_token_count=20,
            tool_invocation_latency={},
            unexpected_extra_key="bad",
        )

from observability_service.evals import EvalScorecard

def test_scorecard_rejects_out_of_bounds():
    with pytest.raises(ValidationError):
        EvalScorecard(
            eval_id="e1", target_trace_id="t1", timestamp=datetime.now(),
            metric_name="m1", score=1.5, evaluator_type="auto")
    with pytest.raises(ValidationError):
        EvalScorecard(
            eval_id="e2", target_trace_id="t2", timestamp=datetime.now(),
            metric_name="m2", score=-0.1, evaluator_type="auto")
