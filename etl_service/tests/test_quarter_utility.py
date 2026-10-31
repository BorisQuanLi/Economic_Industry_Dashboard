"""
Unit tests for etl_service.src.utils.quarter.current_calendar_quarter.

The function is a pure utility with an injection point for ``now``,
so all cases are deterministic — no mocking required.
"""

import re
from datetime import datetime
import pytest
from etl_service.src.utils.quarter import current_calendar_quarter


@pytest.mark.parametrize("month,expected_quarter", [
    (1,  "Q1"),
    (2,  "Q1"),
    (3,  "Q1"),
    (4,  "Q2"),
    (5,  "Q2"),
    (6,  "Q2"),
    (7,  "Q3"),
    (8,  "Q3"),
    (9,  "Q3"),
    (10, "Q4"),
    (11, "Q4"),
    (12, "Q4"),
])
def test_quarter_boundaries(month, expected_quarter):
    result = current_calendar_quarter(now=datetime(2026, month, 15))
    assert result.endswith(expected_quarter), f"month {month}: expected …{expected_quarter}, got {result}"


def test_year_is_included():
    result = current_calendar_quarter(now=datetime(2026, 10, 1))
    assert result.startswith("2026_"), f"Expected year prefix, got {result}"


def test_format_matches_pattern():
    result = current_calendar_quarter(now=datetime(2026, 10, 1))
    assert re.fullmatch(r"\d{4}_Q[1-4]", result), f"Unexpected format: {result}"


def test_defaults_to_current_time():
    """Calling with no argument should not raise and should return a valid label."""
    result = current_calendar_quarter()
    assert re.fullmatch(r"\d{4}_Q[1-4]", result), f"Unexpected format: {result}"
