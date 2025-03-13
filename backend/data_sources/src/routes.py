from flask import Blueprint, jsonify
from app.repositories import CompanyRepository

api = Blueprint('api', __name__)

@api.route('/companies/<sector>')
def get_companies(sector: str):
    """Get companies in a sector."""
    companies = CompanyRepository().get_companies_by_sector(sector)
    return jsonify([vars(c) for c in companies])

@api.route('/sectors')
def get_sectors():
    """Get all sectors."""
    sectors = CompanyRepository().get_all_sectors()
    return jsonify(sectors)
