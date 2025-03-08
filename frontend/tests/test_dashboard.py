import pytest
from dashboard.components import SectorOverview, CompanyList

def test_sector_overview_successful_load(mock_api_client, streamlit_test_container):
    overview = SectorOverview(mock_api_client)
    overview.render(streamlit_test_container)
    
    assert len(streamlit_test_container.items) == 3
    assert streamlit_test_container.items[0]['label'] == 'Average Revenue'
    assert streamlit_test_container.items[0]['value'] == 1000

def test_sector_overview_error_handling(mock_error_api_client, streamlit_test_container):
    overview = SectorOverview(mock_error_api_client)
    with pytest.raises(Exception):
        overview.render(streamlit_test_container)

def test_company_list_display(mock_api_client, mock_sector_companies):
    mock_api_client.get_sector_companies.return_value = mock_sector_companies
    company_list = CompanyList(mock_api_client)
    
    companies = company_list.get_companies('Technology')
    assert len(companies) == 3
    assert companies.iloc[0]['company_name'] == 'CompanyA'
