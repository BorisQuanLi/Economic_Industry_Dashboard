"""Economic sector and industry models for ETL."""
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class SectorMetrics:
    """Aggregated sector-level metrics."""
    sector: str
    total_revenue: float
    avg_revenue: float
    total_market_cap: float
    company_count: int
    subsector_breakdown: Dict[str, int]

@dataclass
class FinancialMetrics:
    """Financial metrics with validation and calculations."""
    revenue: float
    costs: float
    earnings: float
    period: str
    
    @classmethod
    def from_raw_data(cls, data: Dict[str, Any]) -> 'FinancialMetrics':
        """Create FinancialMetrics from raw financial data."""
        revenue = float(data['revenue'])
        costs = float(data['costs'])
        return cls(
            revenue=revenue,
            costs=costs,
            earnings=revenue - costs,
            period=data['period']
        )