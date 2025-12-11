from fastapi import APIRouter
from typing import List, Dict, Optional
from models.financial import CompanyFinancials

router = APIRouter()

@router.get("/")
async def get_all_sectors_performance(financial_indicator: Optional[str] = None):
    """
    Get aggregated financial performance for all sectors.
    NOTE: This is a mock implementation providing sample data.
    """
    indicator = financial_indicator or "revenue"
    # Mock data in the format the frontend expects
    mock_data = {
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
    return mock_data

@router.get("/search")
async def search_sector_names():
    """
    Get a list of all sector names.
    NOTE: This is a mock implementation providing sample data.
    """
    return {"sector_names": ["Technology", "Healthcare"]}

@router.get("/sub-sectors")
async def get_sub_sectors():
    """
    Get a list of all sub-sector names.
    NOTE: This is a mock implementation providing sample data.
    """
    return {"sub_sector_names": ["Application Software", "Systems Software"]}

@router.get("/performance/{sector_name}")
async def get_sector_performance(sector_name: str):
    """Get sector-level financial performance with sliding window alignment"""
    return {"sector": sector_name, "status": "aligned_data_ready"}

@router.get("/companies/{sector_name}", response_model=List[CompanyFinancials])
async def get_sector_companies(sector_name: str):
    """Get all companies in sector with aligned quarterly data"""
    return []
