from typing import Dict, List, Any, Optional
from backend.etl.transform.models.industry.sector_financial_average_model import SectorQuarterlyAverageFinancials
from backend.etl.transform.models.industry.subindustry_financial_average_model import SubIndustryQuarterlyAverageFinancials
from backend.etl.transform.models.company.company_info_model import CompanyInfo

class IndustryAnalysisService:
    """Service for analyzing industry and sector data."""
    
    def __init__(self, cursor):
        self.cursor = cursor

    def get_all_sectors(self) -> List[Dict[str, str]]:
        """Get all distinct sectors from sub_industries table."""
        sql_query = """
            SELECT DISTINCT sector_gics as gics, 
                   sector_name as name
            FROM sub_industries
            ORDER BY sector_name;
        """
        self.cursor.execute(sql_query)
        return [{'gics': row['gics'], 'name': row['name']} for row in self.cursor.fetchall()]

    def get_sector_metrics(self, sector_gics: str) -> Dict[str, Any]:
        """Get financial metrics for a sector."""
        financials = SectorQuarterlyAverageFinancials.calculate_sector_average_quarterly_financials(
            sector_gics, self.cursor
        )
        return financials.to_dict() if financials else {}

    def get_sector_pe_metrics(self, sector_gics: str) -> Dict[str, float]:
        """Get P/E ratio metrics for a sector by its GICS name."""
        return SectorQuarterlyAverageFinancials.calculate_quarter_end_sector_average_pe_ratio(
            sector_gics, self.cursor
        )

    def get_subsectors_by_sector(self, sector_gics: str) -> List[Dict[str, str]]:
        """Get all sub-industries in a sector by the sector's GICS name."""
        return SubIndustryQuarterlyAverageFinancials.get_sub_industries_in_sector(
            sector_gics, self.cursor
        )

    def get_subsector_analytics(self, subsector_gics: str) -> Dict[str, Any]:
        """Get comprehensive analytics for a sub-industry by its GICS name."""
        # Get detailed financial metrics with quarterly history
        financial_avg = SubIndustryQuarterlyAverageFinancials.calculate_subindustry_average_quarterly_financials(
            subsector_gics, self.cursor
        )
        
        if not financial_avg:
            return {}
            
        companies = CompanyInfo.get_companies_in_sub_industry(subsector_gics, self.cursor)
        concentration = SubIndustryQuarterlyAverageFinancials.calculate_industry_concentration(
            subsector_gics, "revenue", self.cursor
        )
        
        top_revenue = SubIndustryQuarterlyAverageFinancials.get_top_performers(
            subsector_gics, "revenue", self.cursor
        )
        top_profit_margin = SubIndustryQuarterlyAverageFinancials.get_top_performers(
            subsector_gics, "profit_margin", self.cursor
        )

        quarters, revenues, net_incomes = [], [], []
        eps_values, profit_margins, pe_ratios = [], [], []
        
        if financial_avg.quarterly_averages:
            for q_avg in financial_avg.quarterly_averages:
                quarters.append(q_avg.quarter)
                revenues.append(q_avg.quarterly_avg_revenue)
                net_incomes.append(q_avg.quarterly_avg_net_income)
                eps_values.append(q_avg.quarterly_avg_earnings_per_share)
                profit_margins.append(q_avg.quarterly_avg_profit_margin if q_avg.quarterly_avg_profit_margin else 0)
                pe_ratios.append(q_avg.quarterly_avg_price_earnings_ratio if q_avg.quarterly_avg_price_earnings_ratio else 0)
        
        return {
            'sub_industry': subsector_gics,
            'quarterly_avg_revenue': financial_avg.quarterly_avg_revenue,
            'quarterly_avg_net_income': financial_avg.quarterly_avg_net_income,
            'quarterly_avg_price_earnings_ratio': financial_avg.quarterly_avg_price_earnings_ratio,
            'concentration_index': concentration,
            'company_count': len(companies),
            'top_performers': {
                'revenue': top_revenue,
                'profit_margin': top_profit_margin
            },
            'quarterly_history': {
                'quarters': quarters,
                'revenues': revenues,
                'net_incomes': net_incomes,
                'eps_values': eps_values,
                'profit_margins': profit_margins,
                'pe_ratios': pe_ratios
            }
        }

    def get_quarterly_analysis(self, data: List[Dict[str, Any]], metric: str) -> List[Dict[str, Any]]:
        """Calculate growth rates for quarterly data."""
        if not data or len(data) < 2:
            return []
            
        results = []
        for i in range(1, len(data)):
            current = data[i].get(metric, 0)
            previous = data[i-1].get(metric, 0)
            
            growth = ((current - previous) / previous) * 100 if previous and previous != 0 else 0
                
            results.append({
                'period': data[i].get('period', ''),
                'growth_rate': round(growth, 2)
            })
            
        return results
    
    def get_pe_analysis(self, sector_id: int) -> Dict[str, Any]:
        """Get P/E analysis for a sector."""
        return SectorQuarterlyAverageFinancials.calculate_quarter_end_sector_average_pe_ratio(
            sector_id, self.cursor
        )

class IndustryAnalyzer:
    """Industry data analysis service."""
    
    def __init__(self, db_connection):
        self.cursor = db_connection.cursor()

    def get_sector_metrics(self, sector_gics: str) -> Dict[str, Any]:
        """Get financial metrics for a sector."""
        financials = SectorQuarterlyAverageFinancials.calculate_sector_average_quarterly_financials(
            sector_gics, self.cursor
        )
        return financials.to_dict() if financials else {}

    def get_subsector_metrics(self, subsector_gics: str) -> Dict[str, Any]:
        """Get financial metrics for a subsector."""
        financials = SubIndustryQuarterlyAverageFinancials.calculate_subindustry_average_quarterly_financials(
            subsector_gics, self.cursor
        )
        return financials.to_dict() if financials else {}
