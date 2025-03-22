"""Company-related endpoints."""
from flask import Blueprint, jsonify, current_app, request, abort

company_bp = Blueprint('companies', __name__, url_prefix='/companies')

@company_bp.route('', methods=['GET'])
def get_companies():
    """Get all companies with optional filtering."""
    db_connection = current_app.config.get('services', {}).get('db_connection')
    if not db_connection:
        return jsonify({'error': 'Database service not available'}), 503
    
    # Extract query parameters for filtering
    sector = request.args.get('sector')
    sub_industry = request.args.get('sub_industry')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)
    
    try:
        # Build the SQL query based on filters
        query = "SELECT id, name, ticker, sub_industry_id FROM companies"
        params = []
        
        if sector or sub_industry:
            query += " JOIN sub_industries ON companies.sub_industry_id = sub_industries.id WHERE "
            
            conditions = []
            if sector:
                conditions.append("sub_industries.sector_gics = %s")
                params.append(sector)
            if sub_industry:
                conditions.append("sub_industries.sub_industry_gics = %s")
                params.append(sub_industry)
                
            query += " AND ".join(conditions)
        
        # Add pagination
        query += f" ORDER BY name LIMIT {limit} OFFSET {offset}"
        
        # Execute query
        cursor = db_connection.cursor
        cursor.execute(query, tuple(params) if params else None)
        companies = cursor.fetchall()
        
        return jsonify({
            'companies': companies,
            'count': len(companies),
            'limit': limit,
            'offset': offset
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/<int:company_id>', methods=['GET'])
def get_company(company_id):
    """Get detailed information about a specific company."""
    analyzer = current_app.config.get('services', {}).get('industry_analyzer')
    if not analyzer:
        return jsonify({'error': 'Service not available'}), 503
    
    try:
        company_data = analyzer.get_company_data(company_id)
        if not company_data:
            return jsonify({'error': 'Company not found'}), 404
            
        return jsonify(company_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/<int:company_id>/financials', methods=['GET'])
def get_company_financials(company_id):
    """Get financial data for a company."""
    analyzer = current_app.config.get('services', {}).get('industry_analyzer')
    if not analyzer:
        return jsonify({'error': 'Service not available'}), 503
    
    time_period = request.args.get('period', 'quarterly')  # quarterly, annual
    
    try:
        financial_data = analyzer.get_company_financials(company_id, time_period=time_period)
        if not financial_data:
            return jsonify({'error': 'Company financial data not found'}), 404
            
        return jsonify(financial_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@company_bp.route('/<int:company_id>/pe_history', methods=['GET'])
def get_company_pe_history(company_id):
    """Get historical P/E ratio data for a company."""
    analyzer = current_app.config.get('services', {}).get('industry_analyzer')
    if not analyzer:
        return jsonify({'error': 'Service not available'}), 503
    
    # Get optional query parameters
    months = request.args.get('months', 12, type=int)
    
    try:
        pe_data = analyzer.get_company_pe_history(company_id, months=months)
        if pe_data is None:
            return jsonify({'error': 'Company not found'}), 404
            
        return jsonify(pe_data)
    except Exception as e:
        return jsonify({'error': str(e)}), 500
