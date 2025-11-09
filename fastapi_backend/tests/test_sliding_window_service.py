import pytest
from fastapi_backend.services.sliding_window import SlidingWindowService

@pytest.mark.asyncio
async def test_get_aligned_sector_performance():
    """Test sliding window service returns aligned data"""
    service = SlidingWindowService()
    result = await service.get_aligned_sector_performance()

    assert len(result) == 1
    assert result[0].aligned_quarter == "2025Q3"
    assert result[0].companies_count == 4
    assert result[0].avg_revenue > 0
