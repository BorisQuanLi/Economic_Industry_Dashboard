from fastapi import APIRouter, Depends
from typing import List
from ..models.financial import SlidingWindowAnalytics
from ..services.sliding_window import SlidingWindowService

router = APIRouter()

@router.get("/sliding-window", response_model=List[SlidingWindowAnalytics])
async def get_sliding_window_analytics():
    """Real-time cross-sector analysis with earnings alignment"""
    service = SlidingWindowService()
    return await service.get_aligned_sector_performance()
