"""Model for calculating average financial metrics for sub-industries."""
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from etl.transform.models.company.company_quarterly_report_model import CompanyQuarterlyReport
from etl.transform.models.company.company_price_earnings_model import PriceEarningsRatio
from etl.transform.models.company.company_info_model import CompanyInfo

@dataclass
class SubIndustryFinancialAverage:
    """Financial averages for a sub-industry."""
    sub_industry_id: int
    sub_industry_name: str
    average_revenue: float
    average_net_income: float
    average_pe_ratio: float
    quarterly_averages: Optional[List['SubIndustryQuarterlyAverage']] = None
    
    @classmethod
    def get_sub_industry_averages(cls, sub_industry_name: str, metric: str, cursor) -> Dict[str, float]:
        """Calculate sub-industry averages for specified metric."""
        # Implementation matches the existing class
        sql_query = f"""
            SELECT AVG({metric}) as avg_value,
                   DATE_TRUNC('quarter', date) as quarter
            FROM quarterly_reports qr
            JOIN companies c ON c.id = qr.company_id
            JOIN sub_industries si ON c.sub_industry_id = si.id
            WHERE si.sub_industry_gics = %s
            GROUP BY quarter
            ORDER BY quarter DESC
            LIMIT 8;
        """
        cursor.execute(sql_query, (sub_industry_name,))
        return {str(r['quarter']): r['avg_value'] for r in cursor.fetchall()}
    
    @classmethod
    def calculate_industry_concentration(cls, sub_industry_name: str, metric: str, cursor) -> float:
        """Calculate industry concentration using Herfindahl-Hirschman Index."""
        # Implementation matches the existing class
        sql_str = f"""
            WITH company_shares AS (
                SELECT 
                    c.id,
                    SUM({metric})::float / SUM(SUM({metric})) OVER () as market_share
                FROM quarterly_reports qr
                JOIN companies c ON c.id = qr.company_id
                JOIN sub_industries si ON c.sub_industry_id = si.id
                WHERE si.sub_industry_gics = %s
                AND qr.date >= NOW() - INTERVAL '12 months'
                GROUP BY c.id
            )
            SELECT SUM(POWER(market_share * 100, 2)) as hhi
            FROM company_shares;
        """
        cursor.execute(sql_str, (sub_industry_name,))
        result = cursor.fetchone()
        return result['hhi'] if result else None
    
    @classmethod
    def get_top_performers(cls, sub_industry_name: str, metric: str, cursor, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing companies in a sub-industry by metric."""
        # Implementation matches the existing class
        sql_str = f"""
            SELECT 
                c.name,
                c.ticker,
                AVG({metric}) as avg_value
            FROM quarterly_reports qr
            JOIN companies c ON c.id = qr.company_id
            JOIN sub_industries si ON c.sub_industry_id = si.id
            WHERE si.sub_industry_gics = %s
            AND qr.date >= NOW() - INTERVAL '12 months'
            GROUP BY c.id, c.name, c.ticker
            ORDER BY avg_value DESC
            LIMIT %s;
        """
        cursor.execute(sql_str, (sub_industry_name, limit))
        return cursor.fetchall()
    
    @classmethod
    def calculate_averages(cls, sub_industry_id: int, cursor) -> 'SubIndustryFinancialAverage':
        """Calculate average financial metrics for a sub-industry."""
        # Get sub-industry name
        cursor.execute(
            "SELECT sub_industry_gics FROM sub_industries WHERE id = %s", 
            (sub_industry_id,)
        )
        result = cursor.fetchone()
        sub_industry_name = result['sub_industry_gics'] if result else "Unknown"
        
        # Use our own method for sub-industry averages
        revenue_data = cls.get_sub_industry_averages(sub_industry_name, "revenue", cursor)
        net_income_data = cls.get_sub_industry_averages(sub_industry_name, "net_income", cursor)
        
        # Get PE ratios for all companies in this sub-industry
        companies = CompanyInfo.get_companies_in_sub_industry(sub_industry_name, cursor)
        pe_values = []
        
        for company in companies:
            avg_pe = PriceEarningsRatio.calculate_average_pe(company['id'], cursor)
            if avg_pe:
                pe_values.append(avg_pe)
        
        # Calculate averages from the latest quarter
        avg_revenue = 0
        avg_net_income = 0
        
        if revenue_data:
            latest_quarter = list(revenue_data.keys())[0]  # First key is the latest quarter
            avg_revenue = revenue_data[latest_quarter]
            
        if net_income_data:
            latest_quarter = list(net_income_data.keys())[0]
            avg_net_income = net_income_data[latest_quarter]
        
        avg_pe = sum(pe_values) / len(pe_values) if pe_values else 0
        
        return cls(
            sub_industry_id=sub_industry_id,
            sub_industry_name=sub_industry_name,
            average_revenue=avg_revenue,
            average_net_income=avg_net_income,
            average_pe_ratio=avg_pe
        )

    @classmethod
    def get_formatted_quarterly_averages(cls, sub_industry_name, cursor):
        """
        Get formatted quarterly averages for a sub-industry.
        
        Args:
            sub_industry_name (str): The sub-industry name
            cursor: Database cursor
            
        Returns:
            list: List of quarterly averages
        """
        # Query quarterly financial data
        cursor.execute("""
            SELECT quarter_label, 
                   avg_revenue, 
                   avg_net_income, 
                   avg_eps, 
                   avg_profit_margin
            FROM sub_industry_quarterly_financial_averages
            WHERE sub_industry_name = %s
            ORDER BY quarter_end DESC
        """, (sub_industry_name,))
        
        financial_data = cursor.fetchall()
        
        # Query quarterly PE ratio data
        cursor.execute("""
            SELECT quarter_label, avg_pe_ratio
            FROM sub_industry_quarter_end_pe_ratio
            WHERE sub_industry_name = %s
            ORDER BY quarter_end DESC
        """, (sub_industry_name,))
        
        pe_data = cursor.fetchall()
        
        # Combine the data
        quarters = []
        for fin in financial_data:
            quarter = {
                'quarter': fin['quarter_label'],
                'avg_revenue': fin['avg_revenue'],
                'avg_net_income': fin['avg_net_income'],
                'avg_eps': fin['avg_eps'],
                'avg_profit_margin': fin['avg_profit_margin'],
                'avg_pe_ratio': 0
            }
            
            # Find matching PE data
            for pe in pe_data:
                if pe['quarter_label'] == fin['quarter_label']:
                    quarter['avg_pe_ratio'] = pe['avg_pe_ratio']
                    break
                    
            quarters.append(quarter)
            
        return quarters

@dataclass
class SubIndustryQuarterlyAverage:
    """Represents quarterly average metrics for a sub-industry."""
    quarter: str  # Formatted as "yyyy-QQ" (e.g., "2023-Q1")
    revenue: float
    net_income: float
    earnings_per_share: float
    profit_margin: float
    price_earnings_ratio: Optional[float] = None

@dataclass
class SubIndustryQuarterlyAverageFinancials:
    """Represents average quarterly financial metrics for a sub-industry."""
    quarter: str  # Formatted as "yyyy-QQ" (e.g., "2023-Q1")
    sub_industry_name: str
    quarterly_avg_revenue: float
    quarterly_avg_net_income: float
    quarterly_avg_earnings_per_share: float
    quarterly_avg_profit_margin: Optional[float]
    quarterly_avg_price_earnings_ratio: Optional[float]
    quarterly_averages: Optional[List['SubIndustryQuarterlyAverageFinancials']] = None
    
    @classmethod
    def get_sub_industry_averages(cls, sub_industry_name: str, metric: str, cursor) -> Dict[str, float]:
        """Calculate sub-industry averages for specified metric."""
        sql_query = f"""
            SELECT AVG({metric}) as avg_value,
                   DATE_TRUNC('quarter', date) as quarter
            FROM quarterly_reports qr
            JOIN companies c ON c.id = qr.company_id
            JOIN sub_industries si ON c.sub_industry_id = si.id
            WHERE si.sub_industry_gics = %s
            GROUP BY quarter
            ORDER BY quarter DESC
            LIMIT 8;
        """
        cursor.execute(sql_query, (sub_industry_name,))
        return {str(r['quarter']): r['avg_value'] for r in cursor.fetchall()}
    
    @classmethod
    def calculate_industry_concentration(cls, sub_industry_name: str, metric: str, cursor) -> float:
        """Calculate industry concentration using Herfindahl-Hirschman Index."""
        sql_str = f"""
            WITH company_shares AS (
                SELECT 
                    c.id,
                    SUM({metric})::float / SUM(SUM({metric})) OVER () as market_share
                FROM quarterly_reports qr
                JOIN companies c ON c.id = qr.company_id
                JOIN sub_industries si ON c.sub_industry_id = si.id
                WHERE si.sub_industry_gics = %s
                AND qr.date >= NOW() - INTERVAL '12 months'
                GROUP BY c.id
            )
            SELECT SUM(POWER(market_share * 100, 2)) as hhi
            FROM company_shares;
        """
        cursor.execute(sql_str, (sub_industry_name,))
        result = cursor.fetchone()
        return result['hhi'] if result else None
        
    @classmethod
    def get_top_performers(cls, sub_industry_name: str, metric: str, cursor, limit: int = 5) -> List[Dict[str, Any]]:
        """Get top performing companies in a sub-industry by metric."""
        sql_str = f"""
            SELECT 
                c.name,
                c.ticker,
                AVG({metric}) as avg_value
            FROM quarterly_reports qr
            JOIN companies c ON c.id = qr.company_id
            JOIN sub_industries si ON c.sub_industry_id = si.id
            WHERE si.sub_industry_gics = %s
            AND qr.date >= NOW() - INTERVAL '12 months'
            GROUP BY c.id, c.name, c.ticker
            ORDER BY avg_value DESC
            LIMIT %s;
        """
        cursor.execute(sql_str, (sub_industry_name, limit))
        return cursor.fetchall()

    @classmethod
    def calculate_averages(cls, sub_industry_name: str, cursor) -> 'SubIndustryQuarterlyAverageFinancials':
        """Calculate average financial metrics for a sub-industry."""
        # Use our own method for sub-industry averages
        revenue_data = cls.get_sub_industry_averages(sub_industry_name, "revenue", cursor)
        net_income_data = cls.get_sub_industry_averages(sub_industry_name, "net_income", cursor)
        
        # Get PE ratios for all companies in this sub-industry
        companies = CompanyInfo.get_companies_in_sub_industry(sub_industry_name, cursor)
        pe_values = []
        
        for company in companies:
            avg_pe = PriceEarningsRatio.calculate_average_pe(company['id'], cursor)
            if avg_pe:
                pe_values.append(avg_pe)
        
        # Calculate averages from the latest quarter
        avg_revenue = 0
        avg_net_income = 0
        
        if revenue_data:
            latest_quarter = list(revenue_data.keys())[0]  # First key is the latest quarter
            avg_revenue = revenue_data[latest_quarter]
            
        if net_income_data:
            latest_quarter = list(net_income_data.keys())[0]
            avg_net_income = net_income_data[latest_quarter]
        
        avg_pe = sum(pe_values) / len(pe_values) if pe_values else 0
        
        return cls(
            quarter="Latest", # Using 'Latest' as a marker for the most recent quarter summary
            sub_industry_name=sub_industry_name,
            quarterly_avg_revenue=avg_revenue,
            quarterly_avg_net_income=avg_net_income,
            quarterly_avg_earnings_per_share=0,  # This needs to be calculated
            quarterly_avg_profit_margin=None,
            quarterly_avg_price_earnings_ratio=avg_pe
        )

    @classmethod
    def get_formatted_quarterly_averages(cls, sub_industry_name: str, cursor, quarters: int = 8) -> List['SubIndustryQuarterlyAverageFinancials']:
        """
        Calculate comprehensive quarterly averages for a sub-industry with properly formatted quarter labels.
        
        Returns a list of SubIndustryQuarterlyAverageFinancials objects for the most recent quarters.
        """
        # First query gets all financial metrics by quarter
        financial_sql = """
            SELECT 
                TO_CHAR(DATE_TRUNC('quarter', qr.date), 'YYYY-"Q"Q') as quarter_label,
                DATE_TRUNC('quarter', qr.date) as quarter_date,
                AVG(qr.revenue) as avg_revenue,
                AVG(qr.net_income) as avg_net_income,
                AVG(qr.earnings_per_share) as avg_eps,
                AVG(qr.profit_margin) as avg_profit_margin
            FROM quarterly_reports qr
            JOIN companies c ON c.id = qr.company_id
            JOIN sub_industries si ON c.sub_industry_id = si.id
            WHERE si.sub_industry_gics = %s
            GROUP BY quarter_label, quarter_date
            ORDER BY quarter_date DESC
            LIMIT %s;
        """
        cursor.execute(financial_sql, (sub_industry_name, quarters))
        financial_data = cursor.fetchall()
        
        # Get PE ratios by quarter - need to join quarterly reports for EPS with price data
        pe_sql = """
            SELECT 
                TO_CHAR(DATE_TRUNC('quarter', pe.date), 'YYYY-"Q"Q') as quarter_label,
                AVG(pe.quarter_end_closing_price / NULLIF(qr.earnings_per_share, 0)) as avg_pe_ratio
            FROM prices_pe pe
            JOIN companies c ON c.id = pe.company_id
            JOIN sub_industries si ON c.sub_industry_id = si.id
            JOIN quarterly_reports qr ON qr.company_id = c.id 
                AND DATE_TRUNC('quarter', qr.date) = DATE_TRUNC('quarter', pe.date)
            WHERE si.sub_industry_gics = %s
            AND qr.earnings_per_share <> 0
            GROUP BY quarter_label, DATE_TRUNC('quarter', pe.date)
            ORDER BY DATE_TRUNC('quarter', pe.date) DESC
            LIMIT %s;
        """
        cursor.execute(pe_sql, (sub_industry_name, quarters))
        pe_data = cursor.fetchall()
        
        # Create a dictionary of PE ratios by quarter for easy lookup
        pe_by_quarter = {row['quarter_label']: row['avg_pe_ratio'] for row in pe_data}
        
        # Build the quarterly average objects
        quarterly_averages = []
        for row in financial_data:
            quarter_label = row['quarter_label']
            quarterly_averages.append(cls(
                quarter=quarter_label,
                sub_industry_name=sub_industry_name,
                quarterly_avg_revenue=row['avg_revenue'],
                quarterly_avg_net_income=row['avg_net_income'],
                quarterly_avg_earnings_per_share=row['avg_eps'],
                quarterly_avg_profit_margin=row['avg_profit_margin'],
                quarterly_avg_price_earnings_ratio=pe_by_quarter.get(quarter_label)
            ))
            
        return quarterly_averages

    @classmethod
    def calculate_subindustry_average_quarterly_financials(cls, sub_industry_name: str, cursor) -> 'SubIndustryQuarterlyAverageFinancials':
        """Calculate average quarterly financial metrics for a sub-industry with detailed quarterly data."""
        # Use our own method for sub-industry averages
        revenue_data = cls.get_sub_industry_averages(sub_industry_name, "revenue", cursor)
        net_income_data = cls.get_sub_industry_averages(sub_industry_name, "net_income", cursor)
        
        # Get PE ratios for all companies in this sub-industry
        companies = CompanyInfo.get_companies_in_sub_industry(sub_industry_name, cursor)
        pe_values = []
        
        for company in companies:
            avg_pe = PriceEarningsRatio.calculate_average_pe(company['id'], cursor)
            if avg_pe:
                pe_values.append(avg_pe)
        
        # Calculate averages from the latest quarter
        avg_revenue = 0
        avg_net_income = 0
        
        if revenue_data:
            latest_quarter = list(revenue_data.keys())[0]  # First key is the latest quarter
            avg_revenue = revenue_data[latest_quarter]
            
        if net_income_data:
            latest_quarter = list(net_income_data.keys())[0]
            avg_net_income = net_income_data[latest_quarter]
        
        avg_pe = sum(pe_values) / len(pe_values) if pe_values else 0
        
        # Get detailed quarterly averages
        quarterly_averages = cls.get_formatted_quarterly_averages(sub_industry_name, cursor)
        
        return cls(
            quarter="Latest",  # Using 'Latest' as a marker for the summary
            sub_industry_name=sub_industry_name,
            quarterly_avg_revenue=avg_revenue,
            quarterly_avg_net_income=avg_net_income,
            quarterly_avg_earnings_per_share=0,  # This would need to be properly calculated
            quarterly_avg_profit_margin=None,
            quarterly_avg_price_earnings_ratio=avg_pe,
            quarterly_averages=quarterly_averages
        )