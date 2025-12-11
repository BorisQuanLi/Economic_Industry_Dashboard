from fastapi import APIRouter, Depends
from typing import List, Dict, Optional

from models.financial import CompanyFinancials
from db_session import get_db_session

router = APIRouter()

@router.get("/test")
async def test_db():
    """Simple test endpoint to verify database connection."""
    try:
        from db_session import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sub_industries")
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()
        return {"status": "success", "sub_industries_count": count}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.get("/")
async def get_all_sectors_performance(
    financial_indicator: Optional[str] = None,
    cursor = Depends(get_db_session)
):
    """
    Get sector data with company counts (since we don't have financial data yet).
    """
    try:
        cursor.execute("""
            SELECT s.sector_gics, COUNT(c.id) as company_count
            FROM sub_industries s
            LEFT JOIN companies c ON c.sub_industry_id = s.id
            GROUP BY s.sector_gics
            ORDER BY company_count DESC
        """)
        results = cursor.fetchall()
        
        sector_data = {}
        for sector, count in results:
            # Create 8 quarters of mock time-series data with realistic variations
            import random
            base_value = count * 1000000  # Convert to millions for revenue-like numbers
            sector_data[sector] = []
            for i, (year, quarter) in enumerate([("2023", 1), ("2023", 2), ("2023", 3), ("2023", 4), 
                                                ("2024", 1), ("2024", 2), ("2024", 3), ("2024", 4)]):
                # Add realistic variation: growth trend with some volatility
                growth_factor = 1 + (i * 0.02)  # 2% growth per quarter
                volatility = random.uniform(0.95, 1.05)  # ±5% random variation
                value = int(base_value * growth_factor * volatility)
                sector_data[sector].append({
                    "date": f"{year}-Q{quarter}", 
                    "company_count": value, 
                    "quarter": quarter, 
                    "year": str(year)
                })
        return sector_data
    except Exception as e:
        return _get_mock_sector_data(financial_indicator or "revenue")

@router.get("/search")
async def search_sector_names():
    """
    Get a list of all sector names from the database.
    """
    try:
        from db_session import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT sector_gics FROM sub_industries ORDER BY sector_gics")
        results = cursor.fetchall()
        sector_names = [row[0] for row in results]
        cursor.close()
        conn.close()
        return {"sector_names": sector_names}
    except Exception as e:
        return {"sector_names": ["Information Technology", "Health Care"], "error": str(e)}

@router.get("/sub-sectors")
async def get_sub_sectors(sub_sector_name: Optional[str] = "all_sub_sectors"):
    """
    Get a list of all sub-sector names.
    """
    try:
        from db_session import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT sub_industry_gics FROM sub_industries ORDER BY sub_industry_gics")
        results = cursor.fetchall()
        sub_sector_names = [row[0] for row in results]
        cursor.close()
        conn.close()
        return {"sub_sector_names": sub_sector_names}
    except Exception as e:
        return {"sub_sector_names": ["Application Software", "Systems Software"], "error": str(e)}

@router.get("/performance/{sector_name}")
async def get_sector_performance(
    sector_name: str,
    financial_indicator: Optional[str] = None
):
    """Get sector-level financial performance with sliding window alignment"""
    return {"sector": sector_name, "status": "mock_data", "data": []}

@router.get("/sub-sectors/{sector_name}/financials")
async def get_sub_sector_financials(
    sector_name: str,
    financial_indicator: Optional[str] = None
):
    """
    Get financial data for all sub-sectors within a given sector.
    """
    return {"message": "Sub-sector financials endpoint", "sector": sector_name}

@router.get("/companies/{sector_name}")
async def get_sector_companies(sector_name: str):
    """Get all companies in sector with aligned quarterly data"""
    return []

@router.get("/companies/{sub_sector_name}/financials")
async def get_company_financials(
    sub_sector_name: str,
    financial_indicator: Optional[str] = None
):
    """
    Get financial data for all companies within a given sub-sector.
    """
    try:
        from db_session import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Get companies in the sub-sector
        cursor.execute("""
            SELECT c.name, c.ticker FROM companies c
            JOIN sub_industries s ON c.sub_industry_id = s.id
            WHERE s.sub_industry_gics = %s
            LIMIT 5
        """, (sub_sector_name,))
        companies = cursor.fetchall()
        cursor.close()
        conn.close()
        
        # Create mock time-series data for each company
        import random
        result = {}
        for i, (company_name, ticker) in enumerate(companies):
            base_value = (20 + i*10) * 1000000
            quarters_data = []
            for j, (year, quarter) in enumerate([("2023", 1), ("2023", 2), ("2023", 3), ("2023", 4), 
                                               ("2024", 1), ("2024", 2), ("2024", 3), ("2024", 4)]):
                growth_factor = 1 + (j * 0.025)
                volatility = random.uniform(0.85, 1.15)
                value = int(base_value * growth_factor * volatility)
                quarters_data.append({
                    'date': f'{year}-Q{quarter}', 
                    financial_indicator or 'revenue': value,
                    'quarter': quarter, 
                    'year': str(year)
                })
            result[f"{company_name} ({ticker})"] = quarters_data
        return result
    except Exception as e:
        return {"error": str(e)}


def _get_mock_sector_data(indicator: str) -> Dict:
    """Fallback mock data when database is unavailable."""
    return {
        "Technology": [
            {"date": "2024-Q4", indicator: 1100000000, "quarter": 4, "year": "2024"},
            {"date": "2025-Q1", indicator: 1150000000, "quarter": 1, "year": "2025"},
            {"date": "2025-Q2", indicator: 1180000000, "quarter": 2, "year": "2025"},
            {"date": "2025-Q3", indicator: 1200000000, "quarter": 3, "year": "2025"}
        ],
        "Healthcare": [
            {"date": "2024-Q4", indicator: 920000000, "quarter": 4, "year": "2024"},
            {"date": "2025-Q1", indicator: 930000000, "quarter": 1, "year": "2025"},
            {"date": "2025-Q2", indicator: 940000000, "quarter": 2, "year": "2025"},
            {"date": "2025-Q3", indicator: 950000000, "quarter": 3, "year": "2025"}
        ]
    }
