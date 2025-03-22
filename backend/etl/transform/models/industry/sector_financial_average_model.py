"""Model for calculating average financial metrics for sectors."""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class SectorFinancialAverage:
    """Financial averages for a sector."""
    sector_name: str
    sub_industries: List[Any]  # List of SubIndustry objects
    quarterly_averages: Optional[List['SectorQuarterlyAverage']] = None
    
    @classmethod
    def from_sector(cls, sector_name: str, cursor) -> 'SectorFinancialAverage':
        """Create a SectorFinancialAverage instance from a sector name."""
        from etl.transform.models.industry.subindustry_model import SubIndustry
        
        # Get all sub-industries in this sector
        cursor.execute(
            """SELECT * FROM sub_industries WHERE sector_gics = %s""",
            (sector_name,)
        )
        sub_industries = [SubIndustry(**row) for row in cursor.fetchall()]
        
        return cls(sector_name=sector_name, sub_industries=sub_industries)
    
    @classmethod
    def get_sector_averages(cls, sector_name: str, metric: str, cursor) -> Dict[str, float]:
        """Calculate sector-wide averages for specified metric."""
        sql_query = f"""
            SELECT AVG({metric}) as avg_value,
                   DATE_TRUNC('quarter', date) as quarter
            FROM quarterly_reports qr
            JOIN companies c ON c.id = qr.company_id
            JOIN sub_industries si ON c.sub_industry_id = si.id
            WHERE si.sector_gics = %s
            GROUP BY quarter
            ORDER BY quarter DESC
            LIMIT 8;
        """
        cursor.execute(sql_query, (sector_name,))
        return {str(r['quarter']): r['avg_value'] for r in cursor.fetchall()}
    
    @classmethod
    def get_sub_industries_in_sector(cls, sector_name: str, cursor) -> List[str]:
        """Get all sub-industries in a sector."""
        sql_query = """
            SELECT DISTINCT sub_industry_gics 
            FROM sub_industries
            WHERE sector_gics = %s
            ORDER BY sub_industry_gics;
        """
        cursor.execute(sql_query, (sector_name,))
        records = cursor.fetchall()
        return [record['sub_industry_gics'] for record in records]
    
    def calculate_sector_average_quarterly_financials(self, cursor) -> Dict[str, Any]:
        """Calculate average quarterly financial metrics for a sector."""
        # Use our own method for sector-wide averages
        revenue_data = self.get_sector_averages(self.sector_name, "revenue", cursor)
        net_income_data = self.get_sector_averages(self.sector_name, "net_income", cursor)
        
        # Calculate totals for latest quarter
        total_revenue = 0
        total_net_income = 0
        total_market_cap = 0
        
        if revenue_data:
            latest_quarter = list(revenue_data.keys())[0]  # First key is the latest quarter
            total_revenue = revenue_data[latest_quarter]
        
        if net_income_data:
            latest_quarter = list(net_income_data.keys())[0]
            total_net_income = net_income_data[latest_quarter]
            
        return {
            'sector': self.sector_name,
            'total_revenue': total_revenue,
            'total_net_income': total_net_income,
            'total_market_cap': total_market_cap,
            'sub_industry_count': len(self.sub_industries)
        }
    
    def calculate_quarter_end_sector_average_pe_ratio(self, cursor) -> Dict[str, float]:
        """Calculate average P/E ratio metrics for the sector."""
        pe_ratios = []
        
        # Get all sub-industries in this sector
        sub_industry_names = self.get_sub_industries_in_sector(self.sector_name, cursor)
        
        for sub_industry_name in sub_industry_names:
            # Fetch companies in the sub-industry
            companies = CompanyInfo.get_companies_in_sub_industry(sub_industry_name, cursor)
            
            # Calculate P/E ratios for each company
            for company in companies:
                avg_pe = PriceEarningsRatio.calculate_average_pe(company['id'], cursor)
                if avg_pe:
                    pe_ratios.append(avg_pe)
                    
        if not pe_ratios:
            return {}

        return {
            'avg_pe': sum(pe_ratios) / len(pe_ratios),
            'median_pe': sorted(pe_ratios)[len(pe_ratios) // 2],
            'min_pe': min(pe_ratios),
            'max_pe': max(pe_ratios)
        }
    
    def calculate_sector_average_quarterly_financials_with_history(self, cursor) -> Dict[str, Any]:
        """Calculate average quarterly financial metrics for a sector with historical data."""
        # First get the current financials
        current_financials = self.calculate_sector_average_quarterly_financials(cursor)
        
        # Then get the quarterly history
        quarterly_avgs = SectorFinancialAverage.get_formatted_quarterly_averages(self.sector_name, cursor)
        
        if not quarterly_avgs:
            return current_financials
            
        # Format quarterly data for easy consumption by frontend
        quarters = []
        revenues = []
        net_incomes = []
        eps_values = []
        profit_margins = []
        pe_ratios = []
        
        for q_avg in quarterly_avgs:
            quarters.append(q_avg.quarter)
            revenues.append(q_avg.revenue)
            net_incomes.append(q_avg.net_income)
            eps_values.append(q_avg.earnings_per_share)
            profit_margins.append(q_avg.profit_margin if q_avg.profit_margin else 0)
            pe_ratios.append(q_avg.price_earnings_ratio if q_avg.price_earnings_ratio else 0)
            
        # Add the quarterly history to the current financials
        current_financials['quarterly_history'] = {
            'quarters': quarters,
            'revenues': revenues,
            'net_incomes': net_incomes,
            'eps_values': eps_values,
            'profit_margins': profit_margins,
            'pe_ratios': pe_ratios
        }
        
        return current_financials
    
    @classmethod
    def get_formatted_quarterly_averages(cls, sector_name: str, cursor, quarters: int = 8) -> List['SectorQuarterlyAverage']:
        """
        Calculate comprehensive quarterly averages for a sector with properly formatted quarter labels.
        
        Returns a list of SectorQuarterlyAverage objects for the most recent quarters.
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
            WHERE si.sector_gics = %s
            GROUP BY quarter_label, quarter_date
            ORDER BY quarter_date DESC
            LIMIT %s;
        """
        cursor.execute(financial_sql, (sector_name, quarters))
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
            WHERE si.sector_gics = %s
            AND qr.earnings_per_share <> 0
            GROUP BY quarter_label, DATE_TRUNC('quarter', pe.date)
            ORDER BY DATE_TRUNC('quarter', pe.date) DESC
            LIMIT %s;
        """
        cursor.execute(pe_sql, (sector_name, quarters))
        pe_data = cursor.fetchall()
        
        # Create a dictionary of PE ratios by quarter for easy lookup
        pe_by_quarter = {row['quarter_label']: row['avg_pe_ratio'] for row in pe_data}
        
        # Build the quarterly average objects
        quarterly_averages = []
        for row in financial_data:
            quarter_label = row['quarter_label']
            quarterly_averages.append(SectorQuarterlyAverage(
                quarter=quarter_label,
                revenue=row['avg_revenue'],
                net_income=row['avg_net_income'],
                earnings_per_share=row['avg_eps'],
                profit_margin=row['avg_profit_margin'],
                price_earnings_ratio=pe_by_quarter.get(quarter_label)
            ))
            
        return quarterly_averages

@dataclass
class SectorQuarterlyAverage:
    """Represents quarterly average metrics for a sector."""
    quarter: str  # Formatted as "yyyy-QQ" (e.g., "2023-Q1")
    revenue: float
    net_income: float
    earnings_per_share: float
    profit_margin: float
    price_earnings_ratio: Optional[float] = None

@dataclass
class SectorQuarterlyAverageFinancials:
    """Represents average quarterly financial metrics for a sector."""
    quarter: str  # Formatted as "yyyy-QQ" (e.g., "2023-Q1")
    sector_name: str
    quarterly_avg_revenue: float
    quarterly_avg_net_income: float
    quarterly_avg_earnings_per_share: float
    quarterly_avg_profit_margin: Optional[float] = None
    quarterly_avg_price_earnings_ratio: Optional[float] = None
    quarterly_averages: Optional[List['SectorQuarterlyAverageFinancials']] = None
    
    @classmethod
    def get_sector_averages(cls, sector_name: str, metric: str, cursor) -> Dict[str, float]:
        """Calculate sector-wide averages for specified metric."""
        sql_query = f"""
            SELECT AVG({metric}) as avg_value,
                   DATE_TRUNC('quarter', date) as quarter
            FROM quarterly_reports qr
            JOIN companies c ON c.id = qr.company_id
            JOIN sub_industries si ON c.sub_industry_id = si.id
            WHERE si.sector_gics = %s
            GROUP BY quarter
            ORDER BY quarter DESC
            LIMIT 8;
        """
        cursor.execute(sql_query, (sector_name,))
        return {str(r['quarter']): r['avg_value'] for r in cursor.fetchall()}

    @classmethod
    def get_sub_industries_in_sector(cls, sector_name: str, cursor) -> List[str]:
        """Get all sub-industries in a sector."""
        sql_query = """
            SELECT DISTINCT sub_industry_gics 
            FROM sub_industries
            WHERE sector_gics = %s
            ORDER BY sub_industry_gics;
        """
        cursor.execute(sql_query, (sector_name,))
        records = cursor.fetchall()
        return [record['sub_industry_gics'] for record in records]
    
    @classmethod
    def calculate_quarter_end_sector_average_pe_ratio(cls, sector_name: str, cursor) -> Dict[str, float]:
        """Calculate average P/E ratio metrics for the sector."""
        pe_ratios = []

        # Get all sub-industries in this sector
        sub_industry_names = cls.get_sub_industries_in_sector(sector_name, cursor)
        
        for sub_industry_name in sub_industry_names:
            # Fetch companies in the sub-industry using CompanyInfo
            companies = CompanyInfo.get_companies_in_sub_industry(sub_industry_name, cursor)
            
            # Calculate P/E ratios for each company
            for company in companies:
                avg_pe = PriceEarningsRatio.calculate_average_pe(company['id'], cursor)
                if avg_pe:
                    pe_ratios.append(avg_pe)

        if not pe_ratios:
            return {}

        return {
            'avg_pe': sum(pe_ratios) / len(pe_ratios),
            'median_pe': sorted(pe_ratios)[len(pe_ratios) // 2],
            'min_pe': min(pe_ratios),
            'max_pe': max(pe_ratios)
        }

    @classmethod
    def get_formatted_quarterly_averages(cls, sector_name: str, cursor, quarters: int = 8) -> List['SectorQuarterlyAverageFinancials']:
        """
        Calculate comprehensive quarterly averages for a sector with properly formatted quarter labels.
        
        Returns a list of SectorQuarterlyAverageFinancials objects for the most recent quarters.
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
            WHERE si.sector_gics = %s
            GROUP BY quarter_label, quarter_date
            ORDER BY quarter_date DESC
            LIMIT %s;
        """
        cursor.execute(financial_sql, (sector_name, quarters))
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
            WHERE si.sector_gics = %s
            AND qr.earnings_per_share <> 0
            GROUP BY quarter_label, DATE_TRUNC('quarter', pe.date)
            ORDER BY DATE_TRUNC('quarter', pe.date) DESC
            LIMIT %s;
        """
        cursor.execute(pe_sql, (sector_name, quarters))
        pe_data = cursor.fetchall()
        
        # Create a dictionary of PE ratios by quarter for easy lookup
        pe_by_quarter = {row['quarter_label']: row['avg_pe_ratio'] for row in pe_data}
        
        # Build the quarterly average objects
        quarterly_averages = []
        for row in financial_data:
            quarter_label = row['quarter_label']
            quarterly_averages.append(cls(
                quarter=quarter_label,
                sector_name=sector_name,
                quarterly_avg_revenue=row['avg_revenue'],
                quarterly_avg_net_income=row['avg_net_income'],
                quarterly_avg_earnings_per_share=row['avg_eps'],
                quarterly_avg_profit_margin=row['avg_profit_margin'],
                quarterly_avg_price_earnings_ratio=pe_by_quarter.get(quarter_label)
            ))
            
        return quarterly_averages

    @classmethod
    def calculate_averages(cls, sector_name: str, cursor) -> 'SectorQuarterlyAverageFinancials':
        """Calculate basic average financial metrics for a sector."""
        # Use our own method for sector-wide averages
        revenue_data = cls.get_sector_averages(sector_name, "revenue", cursor)
        net_income_data = cls.get_sector_averages(sector_name, "net_income", cursor)
        
        # Calculate PE ratio averages
        pe_data = cls.calculate_quarter_end_sector_average_pe_ratio(sector_name, cursor)
        avg_pe = pe_data.get('avg_pe', 0)
        
        # Calculate averages from the latest quarter
        avg_revenue = 0
        avg_net_income = 0
        
        if revenue_data:
            latest_quarter = list(revenue_data.keys())[0]  # First key is the latest quarter
            avg_revenue = revenue_data[latest_quarter]
            
        if net_income_data:
            latest_quarter = list(net_income_data.keys())[0]
            avg_net_income = net_income_data[latest_quarter]
            
        return cls(
            quarter="Latest",  # Using 'Latest' as a marker for the summary
            sector_name=sector_name,
            quarterly_avg_revenue=avg_revenue,
            quarterly_avg_net_income=avg_net_income,
            quarterly_avg_earnings_per_share=0,  # This needs to be calculated
            quarterly_avg_profit_margin=None,
            quarterly_avg_price_earnings_ratio=avg_pe
        )

    @classmethod
    def calculate_sector_average_quarterly_financials(cls, sector_name: str, cursor) -> 'SectorQuarterlyAverageFinancials':
        """Calculate comprehensive average quarterly financial metrics for a sector with detailed history."""
        # Use our own method for sector-wide averages
        revenue_data = cls.get_sector_averages(sector_name, "revenue", cursor)
        net_income_data = cls.get_sector_averages(sector_name, "net_income", cursor)
        
        # Calculate PE ratio averages
        pe_data = cls.calculate_quarter_end_sector_average_pe_ratio(sector_name, cursor)
        avg_pe = pe_data.get('avg_pe', 0)
        
        # Calculate averages from the latest quarter
        avg_revenue = 0
        avg_net_income = 0
        
        if revenue_data:
            latest_quarter = list(revenue_data.keys())[0]  # First key is the latest quarter
            avg_revenue = revenue_data[latest_quarter]
            
        if net_income_data:
            latest_quarter = list(net_income_data.keys())[0]
            avg_net_income = net_income_data[latest_quarter]
            
        # Get detailed quarterly averages
        quarterly_averages = cls.get_formatted_quarterly_averages(sector_name, cursor)
        
        return cls(
            quarter="Latest",  # Using 'Latest' as a marker for the summary
            sector_name=sector_name,
            quarterly_avg_revenue=avg_revenue,
            quarterly_avg_net_income=avg_net_income,
            quarterly_avg_earnings_per_share=0,  # This would need to be properly calculated
            quarterly_avg_profit_margin=None,
            quarterly_avg_price_earnings_ratio=avg_pe,
            quarterly_averages=quarterly_averages
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the quarterly average data to a dictionary format for API responses."""
        # First handle the case with no quarterly history
        if not self.quarterly_averages:
            return {
                'sector': self.sector_name,
                'quarter': self.quarter,
                'quarterly_avg_revenue': self.quarterly_avg_revenue,
                'quarterly_avg_net_income': self.quarterly_avg_net_income,
                'quarterly_avg_earnings_per_share': self.quarterly_avg_earnings_per_share,
                'quarterly_avg_profit_margin': self.quarterly_avg_profit_margin,
                'quarterly_avg_price_earnings_ratio': self.quarterly_avg_price_earnings_ratio
            }
        
        # Format quarterly data for easy consumption by frontend
        quarters = []
        revenues = []
        net_incomes = []
        eps_values = []
        profit_margins = []
        pe_ratios = []
        
        for q_avg in self.quarterly_averages:
            quarters.append(q_avg.quarter)
            revenues.append(q_avg.quarterly_avg_revenue)
            net_incomes.append(q_avg.quarterly_avg_net_income)
            eps_values.append(q_avg.quarterly_avg_earnings_per_share)
            profit_margins.append(q_avg.quarterly_avg_profit_margin if q_avg.quarterly_avg_profit_margin else 0)
            pe_ratios.append(q_avg.quarterly_avg_price_earnings_ratio if q_avg.quarterly_avg_price_earnings_ratio else 0)
        
        # Return a complete dictionary with quarterly history
        return {
            'sector': self.sector_name,
            'quarter': self.quarter,
            'quarterly_avg_revenue': self.quarterly_avg_revenue,
            'quarterly_avg_net_income': self.quarterly_avg_net_income,
            'quarterly_avg_earnings_per_share': self.quarterly_avg_earnings_per_share,
            'quarterly_avg_profit_margin': self.quarterly_avg_profit_margin,
            'quarterly_avg_price_earnings_ratio': self.quarterly_avg_price_earnings_ratio,
            'quarterly_history': {
                'quarters': quarters,
                'revenues': revenues,
                'net_incomes': net_incomes,
                'eps_values': eps_values,
                'profit_margins': profit_margins,
                'pe_ratios': pe_ratios
            }
        }