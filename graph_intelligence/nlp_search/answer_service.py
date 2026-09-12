"""Deterministic, citation-preserving answer rendering for the MVP."""
from __future__ import annotations

from graph_intelligence.nlp_search.schemas import AnalystAnswer, RetrievedRecord


class DeterministicAnswerService:
    """Render retrieved records without introducing ungrounded model claims."""

    def render(self, question: str, records: list[RetrievedRecord]) -> AnalystAnswer:
        citations = [record.record_id for record in records]
        if not records:
            return AnalystAnswer(
                question=question,
                answer="No matching companies were found in the available source records.",
                citations=[],
                records=[],
            )

        lines = []
        for record in records:
            data = record.data
            line = (
                f"{record.ticker}: P/E {data['avg_pe_ratio']}, "
                f"revenue ${data['latest_revenue_usd_bn']}B"
            )
            relationship = data.get("relationship")
            if relationship:
                line += f", relationship score {relationship['proximity_score']}"
            lines.append(line)

        return AnalystAnswer(
            question=question,
            answer="Matching companies, ordered by revenue: " + "; ".join(lines) + ".",
            citations=citations,
            records=records,
        )
