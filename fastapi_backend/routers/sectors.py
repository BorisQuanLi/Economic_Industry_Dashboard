from fastapi import APIRouter
from typing import List, Dict
from ..models.financial import CompanyFinancials

router = APIRouter()

@router.get("/performance/{sector_name}")
async def get_sector_performance(sector_name: str):
    """Get sector-level financial performance with sliding window alignment"""
    return {"sector": sector_name, "status": "aligned_data_ready"}

@router.get("/companies/{sector_name}", response_model=List[CompanyFinancials])
async def get_sector_companies(sector_name: str):
    """Get all companies in sector with aligned quarterly data"""
    return []
