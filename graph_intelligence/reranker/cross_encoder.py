from graph_intelligence.reranker.contracts import RerankResult

class CrossEncoderReranker:
    def rerank(self, question: str, candidates: list[dict]) -> list[RerankResult]:
        # Offline mock: deterministic relevance mapping
        sorted_cands = sorted(candidates, key=lambda c: c.get("relevance",0), reverse=True)
        return [RerankResult(record_id=c["id"], ticker=c.get("ticker",""), rerank_score=float(c.get("relevance",0)), confidence=0.85, rationale="mock offline") for c in sorted_cands]
