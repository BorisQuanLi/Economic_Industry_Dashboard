from pydantic import BaseModel
from typing import Optional
from datetime import date

class SlidingWindowAnalytics(BaseModel):
    aligned_quarter: str
    avg_revenue: float
    avg_eps: float
    companies_count: int
    filing_alignment: str

class CompanyFinancials(BaseModel):
    ticker: str
    company_name: str
    revenue: float
    net_income: float
    eps: float
    filing_date: date
    aligned_quarter: str
