from observability_service.traces import TracePayload

def run_validation():
    payload = TracePayload(
        trace_id="test-001",
        service_name="observability",
        workflow_path=["init"],
        prompt_token_count=10,
        completion_token_count=5,
        tool_invocation_latency={"self-check": 0.1},
    )
    print("TracePayload validated:", payload.trace_id)

if __name__ == "__main__":
    run_validation()
