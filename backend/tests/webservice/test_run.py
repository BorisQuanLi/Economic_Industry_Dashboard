import pytest
from unittest.mock import patch, MagicMock
from backend.webservice.run import init_services
from backend.webservice.services.industry_analysis import IndustryAnalyzer
from backend.etl.load.data_persistence.base import DevelopmentConfig
from backend.webservice.factory import create_app

@pytest.fixture
def mock_config():
    config = DevelopmentConfig()
    config.DEBUG = True
    return config

@pytest.fixture
def mock_analyzer():
    analyzer = MagicMock(spec=IndustryAnalyzer)
    analyzer.get_sectors.return_value = ["Technology", "Healthcare"]
    return analyzer

def test_init_services():
    """Test that services are properly initialized"""
    services = init_services()
    
    assert "industry_analyzer" in services
    assert isinstance(services["industry_analyzer"], IndustryAnalyzer)

@patch('backend.webservice.services.industry_analysis.IndustryAnalyzer')
def test_init_services_with_mock(mock_analyzer_class):
    """Test service initialization with mocked analyzer"""
    mock_analyzer_instance = mock_analyzer_class.return_value
    mock_analyzer_instance.get_sectors.return_value = ["Technology", "Healthcare"]
    
    services = init_services()
    assert "industry_analyzer" in services
    assert services["industry_analyzer"] == mock_analyzer_instance

def test_create_app_with_services(mock_config, mock_analyzer):
    """Test app creation with configuration and services"""
    services = {"industry_analyzer": mock_analyzer}
    app = create_app(mock_config, services)
    
    assert app.config["DEBUG"] == True
    
    with app.app_context():
        assert "industry_analyzer" in app.services
        assert app.services["industry_analyzer"] == mock_analyzer

@pytest.mark.integration
def test_app_initialization_integration():
    """Integration test for full app initialization"""
    config = DevelopmentConfig()
    services = init_services()
    app = create_app(config, services)
    
    with app.test_client() as client:
        response = client.get('/health')
        assert response.status_code == 200

@pytest.mark.parametrize("debug_mode", [True, False])
def test_app_debug_configuration(debug_mode, mock_analyzer):
    """Test app configuration with different debug modes"""
    config = DevelopmentConfig()
    config.DEBUG = debug_mode
    services = {"industry_analyzer": mock_analyzer}
    
    app = create_app(config, services)
    assert app.debug == debug_mode

def test_service_availability_in_request_context(mock_config, mock_analyzer):
    """Test service accessibility within request context"""
    services = {"industry_analyzer": mock_analyzer}
    app = create_app(mock_config, services)
    
    with app.test_request_context('/'):
        assert "industry_analyzer" in app.services
        sectors = app.services["industry_analyzer"].get_sectors()
        assert sectors == ["Technology", "Healthcare"]
