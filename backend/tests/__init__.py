import psycopg2 

def get_test_db():
    conn = psycopg2.connect(user = 'postgres',
                password= 'postgres',
                dbname= 'investment_analysis_test')
    return conn

# Initialize tests package
# This file can be empty
