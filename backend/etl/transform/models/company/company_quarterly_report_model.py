"""Model for company quarterly financial reports."""
from dataclasses import dataclass
from typing import Optional, List
from etl.load.db import connection as db

@dataclass
class CompanyQuarterlyReport:
    id: int
    date: str
    company_id: int
    revenue: float
    net_income: float
    earnings_per_share: float
    profit_margin: Optional[float]

    @classmethod
    def find_by_company_id(cls, company_id: int, cursor) -> List['CompanyQuarterlyReport']:
        sql_str = """SELECT * FROM quarterly_reports
                     WHERE company_id = %s
                     ORDER BY date;"""
        cursor.execute(sql_str, (company_id,))
        records = cursor.fetchall()
        return db.build_from_records(cls, records)

    @classmethod
    def find_by_company_ticker(cls, ticker: str, cursor) -> List['CompanyQuarterlyReport']:
        sql_query = """SELECT quarterly_reports.* 
                       FROM quarterly_reports
                       JOIN companies ON companies.id = quarterly_reports.company_id
                       WHERE companies.ticker = %s
                       ORDER BY date;"""
        cursor.execute(sql_query, (ticker,))
        records = cursor.fetchall()
        return db.build_from_records(cls, records)

    @classmethod
    def calculate_growth_rate(cls, company_id: int, metric: str, cursor, periods: int = 4) -> float:
        """Calculate year-over-year growth rate for specified metric."""
        sql_str = f"""
            WITH quarterly_metrics AS (
                SELECT {metric}, 
                       LAG({metric}, {periods}) OVER (ORDER BY date) as prev_value,
                       date
                FROM quarterly_reports
                WHERE company_id = %s
                ORDER BY date DESC
                LIMIT {periods + 1}
            )
            SELECT ((NULLIF({metric}, 0) - NULLIF(prev_value, 0)) * 100.0 / NULLIF(prev_value, 0)) as growth_rate
            FROM quarterly_metrics
            WHERE prev_value IS NOT NULL
            LIMIT 1;
        """
        cursor.execute(sql_str, (company_id,))
        result = cursor.fetchone()
        return result['growth_rate'] if result else None

    @classmethod
    def get_metric_percentile(cls, company_id: int, metric: str, cursor) -> float:
        """Calculate company's percentile for a metric within its sub-industry."""
        sql_str = f"""
            WITH company_metric AS (
                SELECT AVG({metric}) as avg_value
                FROM quarterly_reports qr1
                WHERE qr1.company_id = %s
                AND qr1.date >= NOW() - INTERVAL '12 months'
            )
            SELECT 
                (COUNT(*) FILTER (WHERE sub_metrics.avg_value < company_metric.avg_value) * 100.0 / COUNT(*)) as percentile
            FROM (
                SELECT AVG(qr2.{metric}) as avg_value
                FROM quarterly_reports qr2
                JOIN companies c ON c.id = qr2.company_id
                WHERE c.sub_industry_id = (
                    SELECT sub_industry_id 
                    FROM companies 
                    WHERE id = %s
                )
                AND qr2.date >= NOW() - INTERVAL '12 months'
                GROUP BY qr2.company_id
            ) sub_metrics
            CROSS JOIN company_metric;
        """
        cursor.execute(sql_str, (company_id, company_id))
        result = cursor.fetchone()
        return result['percentile'] if result else None
