import pytest
from services.sliding_window import SlidingWindowService

@pytest.mark.asyncio
async def test_get_aligned_sector_performance():
    """Test sliding window service returns aligned data"""
    service = SlidingWindowService()
    result = await service.get_aligned_sector_performance()

    assert len(result) == 2
    assert result[0].aligned_quarter == "2025Q4_naive"
    assert result[1].aligned_quarter == "2025Q4_aligned"
    assert result[0].companies_count == 5
    assert result[0].avg_revenue > 0
