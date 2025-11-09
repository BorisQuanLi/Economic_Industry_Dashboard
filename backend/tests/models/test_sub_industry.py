import pytest
from unittest.mock import MagicMock
from api.src.models.sub_industry import SubIndustry

def test_value_most_recent_quater(app):
    with app.app_context():
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, 'Semiconductors', 'Information Technology')
        semiconductors = SubIndustry(id=1, sub_industry_GICS='Semiconductors', sector_GICS='Information Technology')
        revenue = semiconductors.get_financial_indicator_by_quarter('revenue', '2020-12-31')
        assert revenue == 1000.0

def test_semiconductors_avg_revenue_2020_4th_qtr(app):
    with app.app_context():
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (1, 'Semiconductors', 'Information Technology')
        semiconductors = SubIndustry(id=1, sub_industry_GICS='Semiconductors', sector_GICS='Information Technology')
        revenue = semiconductors.get_financial_indicator_by_quarter('revenue', '2020-12-31')
        assert revenue == 1000.0

def test_app_sw_avg_revenue_2020_4th_qtr(app):
    with app.app_context():
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = (2, 'Application Software', 'Information Technology')
        app_sw = SubIndustry(id=2, sub_industry_GICS='Application Software', sector_GICS='Information Technology')
        revenue = app_sw.get_financial_indicator_by_quarter('revenue', '2020-12-31')
        assert revenue == 1000.0
