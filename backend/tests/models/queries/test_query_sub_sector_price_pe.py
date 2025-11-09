import pytest
from unittest.mock import MagicMock
from api.src.models.queries.query_sub_sector_price_pe import MixinSubSectorPricePE
from api.src.models.quarterly_aggregation_models.aggregation_by_quarter import QuarterlyPricePE

class MockSubIndustry(MixinSubSectorPricePE):
    __table__ = 'sub_industries'
    def __init__(self, name='Test SubIndustry'):
        self.name = name

    def __str__(self):
        return self.name

def test_get_sub_sector_names_of_sector():
    """
    Test that get_sub_sector_names_of_sector executes the correct SQL
    and returns a list of sub-sector names.
    """
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        ('Sub-Sector A',),
        ('Sub-Sector B',)
    ]
    
    mock_sub_industry = MockSubIndustry()
    result = mock_sub_industry.get_sub_sector_names_of_sector('Technology', mock_cursor)
    
    mock_cursor.execute.assert_called_once()
    assert result == ['Sub-Sector A', 'Sub-Sector B']

def test_create_objs():
    """
    Test that the create_objs method correctly
    creates a QuarterlyPricePE object from a record.
    """
    mock_sub_industry = MockSubIndustry()
    record = (2022, 4, 150.0, 25.0)
    
    result_obj = mock_sub_industry.create_objs(record)
    
    assert isinstance(result_obj, dict)
    assert result_obj['year'] == 2022
    assert result_obj['quarter'] == 4
    assert result_obj['closing_price'] == 150.0
    assert result_obj['price_earnings_ratio'] == 25.0

def test_to_sub_sector_avg_quarterly_price_pe_json():
    """
    Test that to_sub_sector_avg_quarterly_price_pe_json executes the correct SQL
    and returns a list of quarterly average price/PE data.
    """
    mock_cursor = MagicMock()
    mock_cursor.fetchall.return_value = [
        (1, 2022, 4, 150.0, 25.0),
        (1, 2022, 3, 140.0, 23.0)
    ]
    
    mock_sub_industry = MockSubIndustry()
    result = mock_sub_industry.to_sub_sector_avg_quarterly_price_pe_json('Sub-Sector A', mock_cursor)
    
    mock_cursor.execute.assert_called_once()
    assert len(result) == 2
    assert result[0]['year'] == 2022
    assert result[1]['closing_price'] == 140.0
