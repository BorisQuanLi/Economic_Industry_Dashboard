"""Model for company stock price and price-to-earnings ratio data."""
from dataclasses import dataclass
from typing import Optional
from backend.etl.load.db import connection as db

@dataclass
class PriceEarningsRatio:
    """Tracks historical price and P/E ratio data for companies."""
    id: int
    date: str
    company_id: int
    quarter_end_closing_price: float  # Renamed attribute
    price_earnings_ratio: Optional[float]

    columns = ['id', 'company_id', 'date', 'pe_ratio', 'earnings_per_share', 'closing_price', 'quarter_end']
    
    def __init__(self, id=None, company_id=None, date=None, pe_ratio=None,
                 earnings_per_share=None, closing_price=None, quarter_end=None):
        """Initialize a PriceEarningsRatio instance."""
        self.id = id
        self.company_id = company_id
        self.date = date
        self.pe_ratio = pe_ratio
        self.earnings_per_share = earnings_per_share
        self.closing_price = closing_price
        self.quarter_end = quarter_end

    @classmethod
    def find_by_company_id(cls, company_id: int, cursor):
        """Fetch price/PE records for a specific company."""
        sql_str = """SELECT * FROM prices_pe 
                     WHERE company_id = %s
                     ORDER BY date;"""
        cursor.execute(sql_str, (company_id,))
        records = cursor.fetchall()
        return db.build_from_records(cls, records)

    @classmethod
    def find_by_company_ticker(cls, ticker: str, cursor):
        """Fetch price/PE records for a company by its ticker symbol."""
        sql_str = """SELECT prices_pe.* 
                     FROM prices_pe 
                     JOIN companies ON companies.id = prices_pe.company_id
                     WHERE companies.ticker = %s
                     ORDER BY date;"""
        cursor.execute(sql_str, (ticker,))
        records = cursor.fetchall()
        return db.build_from_records(cls, records)

    @classmethod
    def calculate_average_pe(cls, company_id: int, cursor, period_months: int = 12) -> float:
        """Calculate average P/E ratio for a company over a period."""
        sql_str = """
            SELECT AVG(price_earnings_ratio) as avg_pe
            FROM prices_pe 
            WHERE company_id = %s
            AND date >= NOW() - INTERVAL '%s months';
        """
        cursor.execute(sql_str, (company_id, period_months))
        result = cursor.fetchone()
        return result['avg_pe'] if result else None

    @classmethod
    def get_pe_percentile(cls, company_id: int, cursor) -> float:
        """Calculate company's PE percentile within its sub-industry."""
        sql_str = """
            WITH company_pe AS (
                SELECT AVG(pe1.price_earnings_ratio) as avg_pe
                FROM prices_pe pe1
                WHERE pe1.company_id = %s
                AND pe1.date >= NOW() - INTERVAL '12 months'
            )
            SELECT 
                (COUNT(*) FILTER (WHERE sub_pe.avg_pe < company_pe.avg_pe) * 100.0 / COUNT(*)) as percentile
            FROM (
                SELECT AVG(pe2.price_earnings_ratio) as avg_pe
                FROM prices_pe pe2
                JOIN companies c ON c.id = pe2.company_id
                WHERE c.sub_industry_id = (
                    SELECT sub_industry_id 
                    FROM companies 
                    WHERE id = %s
                )
                AND pe2.date >= NOW() - INTERVAL '12 months'
                GROUP BY pe2.company_id
            ) sub_pe
            CROSS JOIN company_pe;
        """
        cursor.execute(sql_str, (company_id, company_id))
        result = cursor.fetchone()
        return result['percentile'] if result else None
