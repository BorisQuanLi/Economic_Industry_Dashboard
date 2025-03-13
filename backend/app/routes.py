from flask import Blueprint, jsonify
from .industry_analysis import IndustryAnalyzer
from etl.transform.models import Company, FinancialMetrics  # Direct import from ETL

web = Blueprint('web', __name__)

@web.route('/companies/<sector>')
def get_companies(sector: str):
    """Get companies in a sector."""
    analyzer = IndustryAnalyzer()
    companies = analyzer.get_subsector_companies(sector)
    return jsonify([vars(c) for c in companies])

@web.route('/metrics/<symbol>')
def get_company_metrics(symbol: str):
    """Get financial metrics for a company."""
    analyzer = IndustryAnalyzer()
    metrics = analyzer.get_company_metrics(symbol)
    return jsonify(vars(metrics))

@web.route('/sectors')
def get_sector_breakdown():
    """Get all sectors and their sub-sectors."""
    analyzer = IndustryAnalyzer()
    breakdown = analyzer.get_sector_breakdown()
    return jsonify(breakdown)

@web.route('/sectors/<sector>/metrics')
def get_sector_analysis(sector: str):
    """Get sector-level analysis."""
    analyzer = IndustryAnalyzer()
    metrics = analyzer.get_sector_metrics(sector)
    return jsonify(vars(metrics))

@web.route('/sectors/<sector>/subsectors/<subsector>')
def get_subsector_analysis(sector: str, subsector: str):
    """Get sub-sector analysis."""
    analyzer = IndustryAnalyzer()
    metrics = analyzer.get_subsector_metrics(sector, subsector)
    return jsonify(vars(metrics))
