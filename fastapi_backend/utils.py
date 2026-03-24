from datetime import date


# Realistic per-indicator base values for mock data
_INDICATOR_BASE = {
    "revenue":              50,   # $50B (sector average)
    "net_income":            5,   # $5B
    "earnings_per_share":        5,   # $5/share
    "profit_margin":            15,   # 15%
    "closing_price":            50,   # $50/share base
    "price_earnings_ratio":     20,   # 20x
}

def indicator_base(indicator: str) -> float:
    return _INDICATOR_BASE.get(indicator, 1_000_000_000)


def get_recent_8_quarters() -> list[tuple[int, int]]:
    """Return the 8 most recently completed calendar quarters as (year, quarter), oldest first."""
    today = date.today()
    year, quarter = today.year, (today.month - 1) // 3  # last completed quarter
    if quarter == 0:
        year, quarter = year - 1, 4
    quarters = []
    for _ in range(8):
        quarters.append((year, quarter))
        quarter -= 1
        if quarter == 0:
            year, quarter = year - 1, 4
    return list(reversed(quarters))
