import psycopg2 

def get_test_db():
    conn = psycopg2.connect(user = 'postgres',
                password= 'postgres',
                dbname= 'investment_analysis')
    return conn