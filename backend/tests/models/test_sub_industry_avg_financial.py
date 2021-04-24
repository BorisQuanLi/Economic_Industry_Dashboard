import pytest
import psycopg2
from api.src.models import Company, SubIndustry, QuarterlyReport, PricePE

conn = psycopg2.connect(dbname= 'investment_analysis_test', user='postgres', password='postgres')
cursor = conn.cursor()

@pytest.fixture
def build_quarterly_report_price_pe_record():
    
