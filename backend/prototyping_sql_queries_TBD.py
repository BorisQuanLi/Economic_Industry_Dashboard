import psycopg2
from api.src.models.quarterly_report import *

conn = psycopg2.connect(database = 'investment_analysis', user = 'postgres', password = 'postgres')
cursor = conn.cursor()


# Jeff Office Hour, 04/06/2021

# group by a tuple that includes quarter
# https://stackoverflow.com/questions/37071631/postgres-group-by-quarter

sql = """SELECT sub_industries.sub_industry_gics, AVG(revenue)  FROM quarterly_reports
                                            JOIN companies
                                            ON companies.id = quarterly_reports.company_id
                                            JOIN sub_industries
                                            ON companies.sub_industry_id::INT = sub_industries.id
                                            GROUP BY (sub_industries.sub_industry_gics, quater?);
                                            """

def revenue_by_company_query(ticker:str):
    """returns in a list a company's revenues in the most recent 5 quarters"""
    query = f"""SELECT revenue FROM quarterly_reports
                JOIN companies 
                ON companies.id = quarterly_reports.company_id
                WHERE companies.ticker = %s;
                """
    cursor.execute(query, (ticker,))
    records = cursor.fetchall()
    revenue_records_list = [record[0] for record in records]
    return revenue_records_list

cvx_revenues = revenue_by_company_query('CVX')
print(f"Chevron, ticker 'CVX', revenue history:")
print(cvx_revenues)
print('_' * 15)

# Question: how to import this module from frontend?

company_revenues_by_sub_industry_query = """SELECT revenue FROM quarterly_reports
                                            JOIN companies 
                                            ON companies.id = quarterly_reports.company_id
                                            JOIN sub_industries
                                            ON companies.sub_industry_id::INT = sub_industries.id                
                                            WHERE sub_industries.sub_industry_gics = 'Integrated Oil & Gas';
                                            """
cursor.execute(company_revenues_by_sub_industry_query)
records = cursor.fetchall()
print('company_revenues_by_sub_industry_query:')
print(records)
print('_' * 15)

groupby_company_query = """SELECT AVG(quarterly_reports.revenue) FROM quarterly_reports
                                            JOIN companies 
                                            ON companies.id = quarterly_reports.company_id
                                            JOIN sub_industries
                                            ON companies.sub_industry_id::INT = sub_industries.id
                                            WHERE sub_industries.sub_industry_gics = 'Integrated Oil & Gas'              
                                            GROUP BY companies.id;
                                            """
cursor.execute(groupby_company_query)
records = cursor.fetchall()
print("groupby_company_query:")
print("(average of company's revenues over 5 quarters; not of all the companies' revenue in each quarter)")
print(records)

# https://stackoverflow.com/questions/21848537/how-to-select-and-average-rows-in-a-table-in-postgresql
groupby_quarters_query = """SELECT AVG(quarterly_reports.revenue) FROM quarterly_reports
                                            JOIN companies 
                                            ON companies.id = quarterly_reports.company_id
                                            JOIN sub_industries
                                            ON companies.sub_industry_id::INT = sub_industries.id
                                            WHERE sub_industries.sub_industry_gics = 'Integrated Oil & Gas'              
                                            GROUP BY companies.id;
                                            """
