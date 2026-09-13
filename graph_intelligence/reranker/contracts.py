from pydantic import BaseModel, Field

class RerankResult(BaseModel):
    record_id: str
    ticker: str
    rerank_score: float = Field(ge=0.0, le=1.0)
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str | None = None
    rank: int | None = None
