"""Industry analysis service for analyzing sectors and companies."""
import logging
from typing import List, Dict, Any, Optional
from backend.etl.transform.models.industry.sector_financial_average_model import SectorQuarterlyAverageFinancials
from backend.etl.transform.models.industry.subindustry_financial_average_model import SubIndustryQuarterlyAverageFinancials
from backend.etl.transform.models.company.company_info_model import CompanyInfo

logger = logging.getLogger(__name__)

class IndustryAnalyzer:
    """Service for analyzing industry and company data."""
    
    def __init__(self, db_connection):
        """Initialize the analyzer with a database connection."""
        self.db_connection = db_connection
        self.cursor = db_connection.cursor if db_connection else None
        
    def get_sectors(self) -> List[Dict[str, Any]]:
        """Get all sectors."""
        try:
            if not self.cursor:
                logger.error("Database cursor not available")
                return []
                
            self.cursor.execute("SELECT id, name, gics_code, description FROM sectors ORDER BY name")
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting sectors: {str(e)}")
            return []
            
    def get_sector_data(self, sector_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed data for a specific sector."""
        try:
            if not self.cursor:
                logger.error("Database cursor not available")
                return None
                
            # Get basic sector information
            self.cursor.execute(
                "SELECT id, name, gics_code, description FROM sectors WHERE id = %s", 
                (sector_id,)
            )
            sector = self.cursor.fetchone()
            if not sector:
                return None
                
            # Get financial metrics for this sector
            metrics = self.get_sector_metrics(sector_id)
            
            # Get sub-industries in this sector
            sub_industries = self.get_sub_industries_by_sector(sector_id)
            
            # Combine all data
            return {
                'sector': sector,
                'metrics': metrics,
                'sub_industries': sub_industries
            }
        except Exception as e:
            logger.error(f"Error getting sector data: {str(e)}")
            return None
            
    def get_sector_metrics(self, sector_id: int, time_period: str = 'quarterly', 
                          metrics: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
        """Get financial metrics for a sector."""
        try:
            if not self.cursor:
                logger.error("Database cursor not available")
                return None
                
            # Verify sector exists
            self.cursor.execute("SELECT gics_code FROM sectors WHERE id = %s", (sector_id,))
            sector_record = self.cursor.fetchone()
            if not sector_record:
                return None
                
            sector_gics = sector_record['gics_code']
            
            # Define metrics to retrieve if not specified
            if not metrics:
                metrics = ['revenue', 'net_income', 'profit_margin', 'pe_ratio']
                
            # Build query based on time period
            time_filter = ""
            if time_period == 'quarterly':
                time_filter = "AND qr.date >= NOW() - INTERVAL '4 quarters'"
            elif time_period == 'annual':
                time_filter = "AND qr.date >= NOW() - INTERVAL '4 years'"
                
            # Query for each metric
            results = {}
            
            if 'revenue' in metrics or 'net_income' in metrics or 'profit_margin' in metrics:
                query = f"""
                    SELECT 
                        TO_CHAR(DATE_TRUNC('quarter', qr.date), 'YYYY-"Q"Q') as quarter,
                        AVG(qr.revenue) as avg_revenue,
                        AVG(qr.net_income) as avg_net_income,
                        AVG(qr.profit_margin) as avg_profit_margin
                    FROM quarterly_reports qr
                    JOIN companies c ON c.id = qr.company_id
                    JOIN sub_industries si ON c.sub_industry_id = si.id
                    WHERE si.sector_gics = %s
                    {time_filter}
                    GROUP BY quarter
                    ORDER BY MIN(qr.date) DESC
                """
                self.cursor.execute(query, (sector_gics,))
                financial_data = self.cursor.fetchall()
                
                # Extract requested metrics
                for metric in ['revenue', 'net_income', 'profit_margin']:
                    if metric in metrics:
                        metric_key = f'avg_{metric}'
                        results[metric] = [
                            {'period': row['quarter'], 'value': row[metric_key]}
                            for row in financial_data
                        ]
            
            if 'pe_ratio' in metrics:
                # Query for PE ratios
                pe_query = f"""
                    SELECT 
                        TO_CHAR(DATE_TRUNC('quarter', pe.date), 'YYYY-"Q"Q') as quarter,
                        AVG(pe.pe_ratio) as avg_pe_ratio
                    FROM prices_pe pe
                    JOIN companies c ON c.id = pe.company_id
                    JOIN sub_industries si ON c.sub_industry_id = si.id
                    WHERE si.sector_gics = %s
                    {time_filter}
                    GROUP BY quarter
                    ORDER BY MIN(pe.date) DESC
                """
                self.cursor.execute(pe_query, (sector_gics,))
                pe_data = self.cursor.fetchall()
                
                results['pe_ratio'] = [
                    {'period': row['quarter'], 'value': row['avg_pe_ratio']}
                    for row in pe_data
                ]
                
            return results
        except Exception as e:
            logger.error(f"Error getting sector metrics: {str(e)}")
            return None
            
    def get_sub_industries_by_sector(self, sector_id: int) -> Optional[List[Dict[str, Any]]]:
        """Get all sub-industries in a sector."""
        try:
            if not self.cursor:
                logger.error("Database cursor not available")
                return None
                
            # Verify sector exists
            self.cursor.execute("SELECT gics_code FROM sectors WHERE id = %s", (sector_id,))
            sector_record = self.cursor.fetchone()
            if not sector_record:
                return None
                
            sector_gics = sector_record['gics_code']
            
            # Get sub-industries
            query = """
                SELECT id, sub_industry_gics, description 
                FROM sub_industries 
                WHERE sector_gics = %s
                ORDER BY sub_industry_gics
            """
            self.cursor.execute(query, (sector_gics,))
            return self.cursor.fetchall()
        except Exception as e:
            logger.error(f"Error getting sub-industries: {str(e)}")
            return None
    
    def get_company_data(self, company_id: int) -> Optional[Dict[str, Any]]:
        """Get detailed data for a specific company."""
        try:
            if not self.cursor:
                logger.error("Database cursor not available")
                return None
                
            # Get basic company information
            query = """
                SELECT c.id, c.name, c.ticker, c.year_founded, c.number_of_employees, c.HQ_state,
                       si.id as sub_industry_id, si.sub_industry_gics, 
                       si.sector_gics
                FROM companies c
                JOIN sub_industries si ON c.sub_industry_id = si.id
                WHERE c.id = %s
            """
            self.cursor.execute(query, (company_id,))
            company = self.cursor.fetchone()
            if not company:
                return None
                
            # Get latest financial data
            latest_financials_query = """
                SELECT * FROM quarterly_reports
                WHERE company_id = %s
                ORDER BY date DESC
                LIMIT 1
            """
            self.cursor.execute(latest_financials_query, (company_id,))
            latest_financials = self.cursor.fetchone()
            
            # Get latest P/E data
            latest_pe_query = """
                SELECT * FROM prices_pe
                WHERE company_id = %s
                ORDER BY date DESC
                LIMIT 1
            """
            self.cursor.execute(latest_pe_query, (company_id,))
            latest_pe = self.cursor.fetchone()
            
            # Combine all data
            return {
                'company': company,
                'latest_financials': latest_financials,
                'latest_pe': latest_pe
            }
        except Exception as e:
            logger.error(f"Error getting company data: {str(e)}")
            return None
    
    def get_company_financials(self, company_id: int, time_period: str = 'quarterly') -> Optional[Dict[str, Any]]:
        """Get financial data for a company."""
        try:
            if not self.cursor:
                logger.error("Database cursor not available")
                return None
                
            # Verify company exists
            self.cursor.execute("SELECT id FROM companies WHERE id = %s", (company_id,))
            if not self.cursor.fetchone():
                return None
                
            # Build query based on time period
            time_filter = ""
            if time_period == 'quarterly':
                time_filter = "AND date >= NOW() - INTERVAL '4 quarters'"
            elif time_period == 'annual':
                time_filter = "AND date >= NOW() - INTERVAL '4 years'"
                
            # Get financial data
            query = f"""
                SELECT 
                    TO_CHAR(DATE_TRUNC('quarter', date), 'YYYY-"Q"Q') as quarter,
                    date,
                    revenue,
                    net_income,
                    earnings_per_share,
                    profit_margin
                FROM quarterly_reports
                WHERE company_id = %s
                {time_filter}
                ORDER BY date DESC
            """
            self.cursor.execute(query, (company_id,))
            financial_data = self.cursor.fetchall()
            
            return {
                'company_id': company_id,
                'financials': financial_data
            }
        except Exception as e:
            logger.error(f"Error getting company financials: {str(e)}")
            return None
    
    def get_company_pe_history(self, company_id: int, months: int = 12) -> Optional[Dict[str, Any]]:
        """Get historical P/E ratio data for a company."""
        try:
            if not self.cursor:
                logger.error("Database cursor not available")
                return None
                
            # Verify company exists
            self.cursor.execute("SELECT id FROM companies WHERE id = %s", (company_id,))
            if not self.cursor.fetchone():
                return None
                
            # Get P/E history
            query = """
                SELECT 
                    date,
                    pe_ratio,
                    earnings_per_share,
                    closing_price
                FROM prices_pe
                WHERE company_id = %s
                AND date >= NOW() - INTERVAL '%s months'
                ORDER BY date DESC
            """
            self.cursor.execute(query, (company_id, months))
            pe_data = self.cursor.fetchall()
            
            return {
                'company_id': company_id,
                'pe_history': pe_data
            }
        except Exception as e:
            logger.error(f"Error getting company P/E history: {str(e)}")
            return None
