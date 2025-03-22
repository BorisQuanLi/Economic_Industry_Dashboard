"""Tests for sector model."""
import pytest
from unittest.mock import MagicMock
from backend.etl.transform.models.industry.sector_model import Sector

def test_sector_creation(sample_sector_data):
    """Test creating a Sector instance."""
    sector = Sector(**sample_sector_data)
    assert sector.id == sample_sector_data['id']
    assert sector.name == sample_sector_data['name']
    assert sector.gics_code == sample_sector_data['gics_code']

def test_find_by_id(mock_cursor, sample_sector_data):
    """Test finding sector by ID."""
    mock_cursor.fetchone.return_value = sample_sector_data
    sector = Sector.find_by_id(1, mock_cursor)
    
    assert sector is not None
    assert sector.id == 1
    mock_cursor.execute.assert_called_once()

def test_find_all(mock_cursor):
    """Test finding all sectors."""
    mock_cursor.fetchall.return_value = [{'id': 1, 'name': 'Tech', 'gics_code': '45'}]
    sectors = Sector.find_all(mock_cursor)
    
    assert len(sectors) == 1
    assert sectors[0].name == 'Tech'
    mock_cursor.execute.assert_called_once()

def test_sector_model(mock_cursor, sample_sector_data):
    """Test basic sector model functionality."""
    # Test implementation
    pass
