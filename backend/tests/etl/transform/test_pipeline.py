"""Tests for the data pipeline."""
import pytest
from unittest.mock import Mock, patch
from backend.etl.pipeline import DataPipeline
from backend.etl.load.data_persistence.base import DevelopmentConfig

@pytest.fixture
def mock_config():
    return DevelopmentConfig()

@pytest.fixture
def mock_cursor():
    return Mock()

def test_pipeline_initialization(mock_config):
    """Test pipeline initializes correctly."""
    with patch('backend.etl.load.data_persistence.local_postgres.LocalPostgresRepository') as mock_repo:
        mock_repo.return_value.cursor = mock_cursor
        pipeline = DataPipeline(mock_config)
        assert pipeline.data_processor is not None
        assert pipeline.industry_service is not None

def test_get_sector_data(mock_config):
    """Test getting sector data."""
    with patch('backend.webservice.services.industry_analysis.IndustryAnalysisService') as mock_service:
        mock_service.return_value.get_sector_metrics.return_value = {
            'sector': 'Technology',
            'metrics': {'revenue': 1000000}
        }
        
        pipeline = DataPipeline(mock_config)
        result = pipeline.get_sector_data('Technology')
        
        assert result['sector'] == 'Technology'
        assert 'metrics' in result
