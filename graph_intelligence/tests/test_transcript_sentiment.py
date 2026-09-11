"""
Test suite for transcript sentiment analysis and LLM-as-a-Judge evaluation.

Offline-safe: executes with USE_MOCK_TRANSCRIPTS=true and USE_MOCK_LLM=true.
Zero live API or database connection requirements.
"""
from __future__ import annotations

import pytest

try:
    from etl_service.src.adapters.earnings_transcript_builder import EarningsTranscriptBuilder
except ImportError:
    EarningsTranscriptBuilder = None

try:
    from fastapi_backend.services.transcript_sentiment_service import (
        TranscriptSentimentService,
        TranscriptAnalysisResult,
        TranscriptSentiment,
        SentimentJudgeEvaluation,
    )
except ImportError:
    TranscriptSentimentService = None


@pytest.mark.skipif(EarningsTranscriptBuilder is None, reason="etl_service not mounted in standalone graph_intelligence container")
class TestEarningsTranscriptBuilder:
    def test_fetch_raw_transcript_returns_mock_content(self):
        builder = EarningsTranscriptBuilder(ticker="AAPL")
        raw = builder.fetch_raw_transcript(quarter=4, year=2025)
        assert isinstance(raw, str)
        assert "Prepared Remarks" in raw
        assert "Q&A" in raw

    def test_section_transcript_splits_prepared_and_qa(self):
        builder = EarningsTranscriptBuilder(ticker="AAPL")
        raw = "=== Prepared Remarks ===\nGood quarter.\n=== Q&A ===\nAnalyst question."
        prepared, qa = builder.section_transcript(raw)
        assert prepared == "=== Prepared Remarks ===\nGood quarter."
        assert qa == "Analyst question."

    def test_get_transcript_sections_returns_expected_keys(self):
        builder = EarningsTranscriptBuilder(ticker="MSFT")
        result = builder.get_transcript_sections(quarter=4, year=2025)
        assert result["ticker"] == "MSFT"
        assert "prepared_remarks" in result
        assert "qa_section" in result


@pytest.mark.skipif(TranscriptSentimentService is None, reason="fastapi_backend not mounted in standalone graph_intelligence container")
class TestTranscriptSentimentService:
    @pytest.mark.asyncio
    async def test_analyze_transcript_returns_structured_result(self):
        service = TranscriptSentimentService()
        result = await service.analyze_transcript(
            ticker="AAPL",
            year=2025,
            quarter=4,
            prepared_remarks="Revenue grew 14% year-over-year.",
            qa_section="Q&A details.",
        )
        assert isinstance(result, TranscriptAnalysisResult)
        assert isinstance(result.sentiment, TranscriptSentiment)
        assert isinstance(result.judge_evaluation, SentimentJudgeEvaluation)

        # Assert sentiment metrics bounds
        assert -1.0 <= result.sentiment.sentiment_score <= 1.0
        assert result.sentiment.forward_guidance_tone in ["positive", "neutral", "cautious"]
        assert len(result.sentiment.key_themes) > 0

        # Assert LLM-as-a-Judge metrics bounds
        assert 0.0 <= result.judge_evaluation.fidelity_score <= 1.0
        assert result.judge_evaluation.reasoning_quality in ["high", "moderate", "low"]
        assert len(result.judge_evaluation.critique) > 0
