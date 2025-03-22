from typing import Dict, Any, Optional, List

from backend.etl.transform.models.company.company_info_model import CompanyInfo
from backend.etl.transform.models.company.company_quarterly_report_model import CompanyQuarterlyReport
from backend.etl.transform.models.company.company_price_earnings_model import PriceEarningsRatio

class CompanyAnalysisService:
    def __init__(self, cursor):
        self.cursor = cursor

    def get_company_by_ticker(self, ticker: str) -> Optional[CompanyInfo]:
        return CompanyInfo.find_by_stock_ticker(ticker, self.cursor)
    
    def get_company_financials(self, company_id: int) -> Dict[str, Any]:
        quarterly_reports = CompanyQuarterlyReport.find_by_company_id(company_id, self.cursor)
        price_earnings_data = PriceEarningsRatio.find_by_company_id(company_id, self.cursor)
        
        return {
            'metrics': {
                'revenue_growth': CompanyQuarterlyReport.calculate_growth_rate(company_id, 'revenue', self.cursor),
                'profit_margin': CompanyQuarterlyReport.get_metric_percentile(company_id, 'profit_margin', self.cursor),
                'pe_ratio': PriceEarningsRatio.calculate_average_pe(company_id, self.cursor),
                'pe_percentile': PriceEarningsRatio.get_pe_percentile(company_id, self.cursor)
            },
            'quarterly_reports': quarterly_reports,
            'price_earnings_history': price_earnings_data
        }

    def get_quarterly_reports_by_ticker(self, ticker: str) -> List[Dict[str, Any]]:
        return CompanyQuarterlyReport.find_by_company_ticker(ticker, self.cursor)

    def get_companies_in_subsector(self, subsector_gics: str) -> List[str]:
        """Get list of company tickers in the given subsector."""
        return CompanyInfo.get_companies_in_sub_industry(subsector_gics, self.cursor)
