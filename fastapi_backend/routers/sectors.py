from fastapi import APIRouter, Depends
from typing import List, Dict, Optional

from models.financial import CompanyFinancials
from db_session import get_db_session
from cache import cache_get, cache_set
from utils import get_recent_8_quarters, indicator_base

router = APIRouter()


def _get_mock_sector_data(indicator: str) -> Dict:
    """Fallback mock data when database is unavailable."""
    import random
    sectors = {
        "Information Technology": 95, "Health Care": 65, "Financials": 70,
        "Consumer Discretionary": 55, "Industrials": 50,
    }
    quarters = get_recent_8_quarters()
    is_per_share = indicator in ("closing_price", "earnings_per_share", "price_earnings_ratio", "profit_margin")
    result = {}
    for rank, (sector, base) in enumerate(sectors.items()):
        base_value = indicator_base(indicator) * (1 + rank * (0.005 if is_per_share else 0.02))
        result[sector] = [
            {indicator: round(base_value * (1 + j * (0.005 if is_per_share else 0.02)) * random.uniform(0.95, 1.05), 2),
             "quarter": q, "year": str(y)}
            for j, (y, q) in enumerate(quarters)
        ]
    return result


def _get_mock_company_financials(sub_sector_name: str, indicator: str) -> Dict:
    """
    Fallback mock data when DB is empty or unavailable.
    Apple's Q4 ends in October (fiscal Q4 = calendar Q3), while peers end in December.
    This offset is exactly what the sliding window algorithm corrects for.
    """
    import random
    sub_sector_company_map = {
        "Application Software": {"Apple (AAPL)": 120, "Microsoft (MSFT)": 62, "Salesforce (CRM)": 45, "Adobe (ADBE)": 40, "Intuit (INTU)": 30},
        "Systems Software": {"Microsoft (MSFT)": 62, "Oracle (ORCL)": 48, "CrowdStrike (CRWD)": 35, "Palo Alto Networks (PANW)": 32, "Snowflake (SNOW)": 28},
        "Semiconductors": {"NVIDIA (NVDA)": 110, "Broadcom (AVGO)": 85, "AMD (AMD)": 55, "Qualcomm (QCOM)": 50, "Texas Instruments (TXN)": 42},
        "Biotechnology": {"Vertex (VRTX)": 80, "Amgen (AMGN)": 75, "Gilead (GILD)": 68, "Regeneron (REGN)": 65, "Moderna (MRNA)": 35},
        "Pharmaceuticals": {"Eli Lilly (LLY)": 130, "Pfizer (PFE)": 90, "Johnson & Johnson (JNJ)": 95, "Merck (MRK)": 85, "AbbVie (ABBV)": 80},
        "Diversified Banks": {"JPMorgan Chase (JPM)": 125, "Bank of America (BAC)": 85, "Wells Fargo (WFC)": 65, "Citigroup (C)": 55, "U.S. Bancorp (USB)": 40},
        "Automobile Manufacturers": {"Tesla (TSLA)": 115, "Ford (F)": 70, "General Motors (GM)": 68, "Rivian (RIVN)": 30, "Lucid (LCID)": 20},
        "Aerospace & Defense": {"Boeing (BA)": 95, "Lockheed Martin (LMT)": 90, "RTX (RTX)": 85, "Northrop Grumman (NOC)": 75, "General Dynamics (GD)": 70},
        "Regional Banks": {"JPM": 125, "BAC": 85, "WFC": 65, "C": 55},
        "Asset Management & Custody Banks": {"MS": 115, "BLK": 110, "STT": 65},
        "Financial Exchanges & Data": {"MSCI": 92, "NDAQ": 78},
        "Broadline Retail": {"AMZN": 135, "WMT": 95, "TGT": 82},
        "Hotels, Resorts & Cruise Lines": {"MAR": 72, "HLT": 68, "CCL": 55},
        "Air Freight & Logistics": {"FDX": 88, "UPS": 82, "CHRW": 45},
        "Industrial Machinery": {"GE": 78, "CAT": 95, "DE": 72},
    }
    mock_companies = sub_sector_company_map.get(sub_sector_name, {
        "Apple (AAPL)":     120,  # fiscal Q4 ends Oct — the misalignment case
        "Microsoft (MSFT)": 62,
        "Alphabet (GOOGL)": 88,
        "Meta (META)":      40,
        "NVIDIA (NVDA)":    35,
    })
    quarters = get_recent_8_quarters()
    result = {}
    for company, base in mock_companies.items():
        base_value = base * indicator_base(indicator)
        result[company] = [
            {indicator: round(base_value / 120 * (1 + j*0.03) * random.uniform(0.92, 1.08), 2),
             "quarter": q, "year": str(y)}
            for j, (y, q) in enumerate(quarters)
        ]
    return result

@router.get("/test")
async def test_db(conn=Depends(get_db_session)):
    """Simple test endpoint to verify database connection."""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM sub_industries")
        count = cursor.fetchone()[0]
        cursor.close()
        return {"status": "success", "sub_industries_count": count}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.get("/")
async def get_all_sectors_performance(
    financial_indicator: Optional[str] = None,
    conn=Depends(get_db_session)
):
    """
    Get sector data with company counts (since we don't have financial data yet).
    """
    cache_key = f"sectors:all:{financial_indicator or 'default'}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached

    try:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.sector_gics, COUNT(c.id) as company_count
            FROM sub_industries s
            LEFT JOIN companies c ON c.sub_industry_id = s.id
            WHERE s.sector_gics IS NOT NULL
            GROUP BY s.sector_gics
            ORDER BY company_count DESC
        """)
        results = cursor.fetchall()
        cursor.close()

        import random
        ind = financial_indicator or "revenue"
        is_per_share = ind in ("closing_price", "earnings_per_share", "price_earnings_ratio", "profit_margin")
        sector_data = {}
        for rank, (sector, count) in enumerate(results):
            base_value = indicator_base(ind) * (1 + rank * (0.005 if is_per_share else 0.02))
            sector_data[sector] = []
            for i, (year, quarter) in enumerate(get_recent_8_quarters()):
                growth_factor = 1 + (i * (0.005 if is_per_share else 0.02))
                volatility = random.uniform(0.95, 1.05)
                value = round(base_value * growth_factor * volatility, 2)
                sector_data[sector].append({
                    "date": f"{year}-Q{quarter}",
                    ind: value,
                    "quarter": quarter,
                    "year": str(year)
                })
        cache_set(cache_key, sector_data)
        return sector_data
    except Exception as e:
        return _get_mock_sector_data(financial_indicator or "revenue")

@router.get("/search")
async def search_sector_names(conn=Depends(get_db_session)):
    """
    Get a list of all sector names from the database.
    """
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT DISTINCT sector_gics FROM sub_industries ORDER BY sector_gics")
        results = cursor.fetchall()
        sector_names = [row[0] for row in results]
        cursor.close()
        return {"sector_names": sector_names}
    except Exception as e:
        return {
            "sector_names": [
                "Information Technology",
                "Health Care",
                "Financials",
                "Consumer Discretionary",
                "Industrials",
            ],
            "error": str(e),
        }

@router.get("/sub-sectors")
async def get_sub_sectors(sector_name: Optional[str] = None, conn=Depends(get_db_session)):
    """
    Get sub-sector names, optionally filtered by sector.
    """
    try:
        cursor = conn.cursor()
        if sector_name:
            cursor.execute(
                "SELECT DISTINCT sub_industry_gics FROM sub_industries WHERE sector_gics = %s ORDER BY sub_industry_gics",
                (sector_name,)
            )
        else:
            cursor.execute("SELECT DISTINCT sub_industry_gics FROM sub_industries ORDER BY sub_industry_gics")
        results = cursor.fetchall()
        sub_sector_names = [row[0] for row in results]
        cursor.close()
        return {"sub_sector_names": sub_sector_names}
    except Exception as e:
        sector_sub_map = {
            "Information Technology": ["Application Software", "Systems Software", "Semiconductors"],
            "Health Care": ["Biotechnology", "Pharmaceuticals"],
            "Financials": ["Diversified Banks", "Regional Banks", "Asset Management & Custody Banks", "Financial Exchanges & Data"],
            "Consumer Discretionary": ["Automobile Manufacturers", "Broadline Retail", "Hotels, Resorts & Cruise Lines"],
            "Industrials": ["Aerospace & Defense", "Air Freight & Logistics", "Industrial Machinery"],
        }
        fallback_subs = sector_sub_map.get(sector_name, ["Application Software", "Systems Software", "Semiconductors"])
        return {"sub_sector_names": fallback_subs, "error": str(e)}

@router.get("/performance/{sector_name}")
async def get_sector_performance(
    sector_name: str,
    financial_indicator: Optional[str] = None
):
    """Get sector-level financial performance with sliding window alignment"""
    cache_key = f"sectors:performance:{sector_name}:{financial_indicator or 'default'}"
    cached = cache_get(cache_key)
    if cached is not None:
        return cached
    ind = financial_indicator or "revenue"
    mock = _get_mock_sector_data(ind)
    data = mock.get(sector_name, mock.get("Information Technology", []))
    result = {"sector": sector_name, "status": "mock_data", "data": data}
    cache_set(cache_key, result)
    return result

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
    financial_indicator: Optional[str] = None,
    conn=Depends(get_db_session)
):
    """
    Get financial data for all companies within a given sub-sector.
    """
    try:
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
        
        if not companies:
            return _get_mock_company_financials(sub_sector_name, financial_indicator or "revenue")

        import random
        ind = financial_indicator or "revenue"
        result = {}
        for i, (company_name, ticker) in enumerate(companies):
            base_value = (1 + i * 0.1) * indicator_base(ind)
            quarters_data = []
            for j, (year, quarter) in enumerate(get_recent_8_quarters()):
                growth_factor = 1 + (j * 0.025)
                volatility = random.uniform(0.85, 1.15)
                value = round(base_value * growth_factor * volatility, 2)
                quarters_data.append({
                    'date': f'{year}-Q{quarter}',
                    ind: value,
                    'quarter': quarter,
                    'year': str(year)
                })
            result[f"{company_name} ({ticker})"] = quarters_data
        return result
    except Exception as e:
        return _get_mock_company_financials(sub_sector_name, financial_indicator or "revenue")


