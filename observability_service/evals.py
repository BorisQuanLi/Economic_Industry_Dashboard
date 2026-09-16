from datetime import datetime
from pydantic import BaseModel, field_validator, ValidationError


class EvalScorecard(BaseModel):
    model_config = {"extra": "forbid"}

    eval_id: str
    target_trace_id: str
    timestamp: datetime
    metric_name: str
    score: float
    evaluator_type: str

    @field_validator("score")
    @classmethod
    def score_bounded(cls, v):
        if not (0.0 <= v <= 1.0):
            raise ValueError("score must be in [0.0, 1.0]")
        return v
