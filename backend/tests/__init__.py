import psycopg2 

def get_test_db():
    conn = psycopg2.connect(user = 'postgres',
                password= 'postgres',
                dbname= 'investment_analysis_test')
    return conn

"""
Test suite for the backend application.
Follows the same structure as the main application:
- api/: Tests for API components
- app/: Tests for application logic
- common/: Shared test utilities
"""
