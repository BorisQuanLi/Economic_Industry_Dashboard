"""
Earnings Transcript Builder — ETL Adapter.

Fetches earnings call transcripts, sectioning content into Prepared Remarks
vs. Analyst Q&A sections for downstream sentiment analysis.

Offline-safe: USE_MOCK_TRANSCRIPTS=true returns deterministic mock fixture data.
"""
from __future__ import annotations

import json
import os
from urllib.request import urlopen
from typing import Dict, Any, Tuple


_MOCK_PREPARED_REMARKS = (
    "Good afternoon, everyone. During the quarter, revenue grew 14% year-over-year "
    "driven by robust enterprise adoption across our SaaS portfolio. Operating margin "
    "expanded 180 basis points to 26.4%. We remain cautious on macroeconomic headwinds "
    "in European commercial real estate, but our forward pipeline remains solid."
)

_MOCK_QA_SECTION = (
    "Question from Analyst: Can you elaborate on the European enterprise softness?\n"
    "Answer: While sales cycles extended slightly in Germany, strategic deals in "
    "North America offset the localized deceleration. We see no systemic churn."
)


class EarningsTranscriptBuilder:
    """
    Adapter for fetching and sectioning earnings call transcripts.
    """

    def __init__(self, ticker: str, conn: Any = None, cursor: Any = None):
        self.conn = conn
        self.cursor = cursor
        self.ticker = ticker

    def fetch_raw_transcript(self, quarter: int = 4, year: int = 2025) -> str:
        """
        Fetches raw transcript string from FMP endpoint or returns offline mock.
        """
        if os.getenv("USE_MOCK_TRANSCRIPTS", "true").lower() == "true":
            return f"=== Prepared Remarks ===\n{_MOCK_PREPARED_REMARKS}\n=== Q&A ===\n{_MOCK_QA_SECTION}"

        api_key = os.getenv("FMP_API_KEY", "")
        url = (
            f"https://financialmodelingprep.com/api/v3/earning_call_transcript/"
            f"{self.ticker}?quarter={quarter}&year={year}&apikey={api_key}"
        )
        try:
            response = urlopen(url, timeout=10)
            data = response.read().decode("utf8")
            records = json.loads(data)
            if isinstance(records, list) and len(records) > 0:
                return str(records[0].get("content", ""))
        except Exception:
            pass

        return f"=== Prepared Remarks ===\n{_MOCK_PREPARED_REMARKS}\n=== Q&A ===\n{_MOCK_QA_SECTION}"

    def section_transcript(self, raw_content: str) -> Tuple[str, str]:
        """
        Splits raw transcript content into (prepared_remarks, qa_section).
        Uses 'Q&A' or 'Question-and-Answer' delimiter.
        """
        delimiters = ["=== Q&A ===", "Question-and-Answer", "Q&A Session", "Questions and Answers", "Q&A"]
        for delim in delimiters:
            if delim in raw_content:
                parts = raw_content.split(delim, 1)
                return parts[0].strip(), parts[1].strip()

        # Fallback: treat top half as prepared remarks, bottom half as Q&A
        midpoint = len(raw_content) // 2
        return raw_content[:midpoint].strip(), raw_content[midpoint:].strip()

    def get_transcript_sections(self, quarter: int = 4, year: int = 2025) -> Dict[str, str]:
        """
        Public entrypoint returning sectioned transcript dictionary.
        """
        raw = self.fetch_raw_transcript(quarter=quarter, year=year)
        prepared, qa = self.section_transcript(raw)
        return {
            "ticker": self.ticker,
            "year": str(year),
            "quarter": str(quarter),
            "prepared_remarks": prepared,
            "qa_section": qa,
        }
