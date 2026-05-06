import strawberry


@strawberry.interface
class Entity:
    """Base type: maps to Guest in Slang's domain, Company in this demo."""
    id: strawberry.ID
    name: str
    is_priority: bool  # VIP guest OR high-value sector (e.g. Health Care in a crisis)


@strawberry.type
class Company(Entity):
    ticker: str
    sector_GICS: str             # dead-letter triage key
    price_earnings_ratio: float


@strawberry.type
class FilingRecord:
    id: strawberry.ID
    ticker: str
    filing_date: str             # raw QuarterlyReport.date (may be Apple Oct)
    aligned_quarter: str         # sliding-window corrected
    revenue: float               # float avoids GraphQL 32-bit Int overflow
    earnings_per_share: float
    report_type: str             # "10-Q" | "8-K"; 8-K triggers human escalation
