"""
Shared utility for calendar-quarter derivation.

Returns the current calendar quarter as a string in the format ``YYYY_QN``
(e.g. ``2026_Q4``), consistent with the ``aligned_quarter`` field used in
the FastAPI ``SlidingWindowAnalytics`` response model.

This is intentionally a pure function with no side-effects so it can be
called at ingestion time (not at module import time) and is trivially
patchable in tests via ``monkeypatch``.
"""

from datetime import datetime


def current_calendar_quarter(now: datetime | None = None) -> str:
    """
    Return the current calendar quarter label, e.g. ``'2026_Q4'``.

    Parameters
    ----------
    now:
        Injection point for the current datetime — pass a fixed value in
        tests to make quarter derivation deterministic.  Defaults to
        ``datetime.now()`` when omitted.
    """
    if now is None:
        now = datetime.now()
    quarter = (now.month - 1) // 3 + 1
    return f"{now.year}_Q{quarter}"
