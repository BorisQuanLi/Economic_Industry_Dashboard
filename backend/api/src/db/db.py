from flask import current_app
from flask import g
import psycopg2
from datetime import datetime, timedelta
from settings import DB_USER, DB_NAME, DB_HOST, DB_PASSWORD, DEBUG, TESTING # backend/settings.py

# Connecting to Postgres on local Mac (parameters hard-coded):
conn = psycopg2.connect(database = 'investment_analysis', user = 'postgres', password = 'postgres')
cursor = conn.cursor()

def get_db():
    if "db" not in g:
        # connect to postgres on the local computer
        g.db = psycopg2.connect(user = 'postgres', password = 'postgres',
            dbname = current_app.config['DB_NAME']) # apply this to user, password in __init__.py (at the top of this script, already imported from SETTINGS)

        """
        # connect to postgres on the AWS RDS instance
        g.db = psycopg2.connect(user = 'postgres', password = 'postgres',
            dbname = current_app.config['DATABASE'])
        """
    return g.db

"""
# Connecting to the AWS RDS instance
conn = psycopg2.connect(host = DB_HOST, database = DB_NAME, 
                        user = DB_USER, password = DB_PASSWORD)  

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(host = DB_HOST, database = DB_NAME, 
                    user = DB_USER, password = DB_PASSWORD) 
    return g.db
"""

def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def build_from_record(Class, record):
    if not record: return None
    attr = dict(zip(Class.columns, record))
    obj = Class()
    obj.__dict__ = attr
    return obj

def build_from_records(Class, records):
   return [build_from_record(Class, record) for record in records]

def find_all(Class, cursor):
    sql_str = f"SELECT * FROM {Class.__table__}"
    cursor.execute(sql_str)
    records = cursor.fetchall()
    return [build_from_record(Class, record) for record in records]

def find(Class, id, cursor):
    sql_str = f"SELECT * FROM {Class.__table__} WHERE id = %s"
    cursor.execute(sql_str, (id,))
    record = cursor.fetchone()
    return build_from_record(Class, record)

def find_companies_by_sub_industry_name(Class, sub_industry_name, cursor):
    """
    params  Class: models.Company
            sub_industry_name: value of the sub_industry_gics column in the sub_industries table

    returns Company objects of all the companies in the same sub_industry
    """
    sql_str = f"""SELECT companies.* FROM companies 
                  JOIN sub_industries
                  ON companies.sub_industry_id::INTEGER = sub_industries.id
                  WHERE sub_industries.sub_industry_gics = %s;
                """
    cursor.execute(sql_str, (sub_industry_name,))
    records = cursor.fetchall()
    return build_from_records(Class, records)

def find_by_ticker(Class, ticker_symbol, cursor):
    search_str = f"""SELECT * FROM {Class.__table__} WHERE ticker = %s;"""
    cursor.execute(search_str, (ticker_symbol,))
    record = cursor.fetchone()
    return build_from_record(Class, record)

def find_company_by_name(company_name, cursor):
    search_str = "SELECT * From companies where name = %$;"
    cursor.execute(search_str, (company_name,))
    record = cursor.fetchone()
    return build_from_record(record)

def find_company_by_ticker(Class, ticker_symbol, cursor):
    sql_str = f"""SELECT * FROM companies
                    WHERE ticker = %s;"""
    cursor.execute(sql_str, (ticker_symbol,))
    record = cursor.fetchone()
    return build_from_record(Class, record)

# 02/02, based on Office Hour discussion with Jeff, to be called by the function that produces multiple quarters' numbers.
def report_dates(cursor):
    sql_str = """
                SELECT date FROM prices_pe 
                WHERE company_id = (
                    SELECT DISTINCT company_id FROM prices_pe LIMIT 1);
                """
    cursor.execute(sql_str)
    report_dates_list = [report_date[0] for report_date in cursor.fetchall()]
    return report_dates_list

def sub_industry_quarterly_avg_numbers(Class, sub_industry_name, report_date, cursor):
    """
    params: 
        sub_industry_name, matches the entry in the sub_industries table
        report_date, string in the "yyyy-mm-dd" format. passed in from either the quarterly_reports or the prices_pe tables, indicating
            the date of the SEC filing that includes the various financials and stock price.

    returns the average value of one quarter's financial numbers from both the quarterly_reports and prices_pe
    table (revenue, net_income, earnings_per_share in the former; closing_price and price_earnings_ratio in the latter).

    Only the raw "row data" from the SQL query, can't be sent to the build_from_records function because
    the data comes from two different classes (SQL tables)?
    """
    
    sql_str = """SELECT ROUND(AVG(prices_pe.closing_price:: numeric), 2) avg_closing_price,
                        ROUND(AVG(prices_pe.price_earnings_ratio:: numeric), 2) avg_pe_ratio,
                        ROUND(AVG(quarterly_reports.revenue:: numeric), 2) avg_revenue,
                        ROUND(AVG(quarterly_reports.net_income:: numeric), 2) avg_net_income
                FROM sub_industries 
                JOIN companies 
                ON sub_industries.id = companies.sub_industry_id::INTEGER
                JOIN prices_pe
                ON prices_pe.company_id = companies.id
                JOIN quarterly_reports
                ON quarterly_reports.company_id = companies.id
                WHERE sub_industries.sub_industry_gics = %s 
                        AND prices_pe.date::DATE > %s
                        AND prices_pe.date::DATE < %s
                GROUP BY sub_industries.id;
                """
    
    lower_date_range = report_date - timedelta(days= 45)
    upper_date_range = report_date + timedelta(days= 45)

    cursor.execute(sql_str, 
                            (sub_industry_name, 
                                lower_date_range, 
                                upper_date_range,))
    single_quarter_numbers = [float(e) for e in cursor.fetchone()]
    single_quarter_record = [report_date.strftime("%Y-%m-%d"), sub_industry_name] + single_quarter_numbers
    return build_from_record(Class, single_quarter_record)


def avg_quarterly_financials_by_sub_industry(Class, sub_industry_name, cursor):
    """
    Param Class: QuarterlyReport
    """
    sql_str = """SELECT ROUND(AVG(revenue)) AS average_revenue, 
                        ROUND(AVG(net_income)) AS average_net_income,
                        ROUND(AVG(earnings_per_share)) AS earnings_per_share, 
                    FROM sub_industries JOIN companies 
                    ON sub_industries.id = companies.sub_industry_id::INTEGER
                    JOIN quarterly_reports
                    ON quarterly_reports.company_id = companies.id
                    WHERE sub_industries.id = 31
                    GROUP BY sub_industries.id;
              """
    cursor.execute(sql_str, (sub_industry_name,))
    record = cursor.fetchone()
    return build_from_record(Class, record)

def avg_quarterly_prices_pe_by_sub_industry(Class, sub_industry_name, cursor):
    """
    Param Class: PricePE
    """
    sql_str = """SELECT ROUND(AVG(closing_price)::numeric, 2) average_closing_price, 
                        ROUND(AVG(price_earnings_ratio)::numeric, 2) average_price_earnings_ratio 
                    FROM sub_industries JOIN companies 
                    ON sub_industries.id = companies.sub_industry_name
                    JOIN prices_pe
                    ON prices_pe.company_id = companies.id
                    WHERE sub_industries.id = 31
                    GROUP BY sub_industries.id;
              """
    cursor.execute(sql_str, (sub_industry_name,))
    record = cursor.fetchone()
    return build_from_record(Class, record)

def find_quarterly_reports_by_ticker(Class, ticker_symbol, cursor):
    sql_str = f"""SELECT * FROM quarterly_reports
                JOIN companies 
                ON companies.id = quarterly_reports.company_id
                WHERE companies.ticker = %s
                ORDER BY quarterly_reports.date
                DESC;
                """
    cursor.execute(sql_str, (ticker_symbol,))
    records = cursor.fetchall()
    return build_from_records(Class, records)

def find_latest_company_price_pe_by_ticker(Class, ticker_symbol, cursor):
    sql_str = f"""SELECT * FROM prices_pe
                JOIN companies 
                ON companies.id = prices_pe.company_id
                WHERE companies.ticker = %s;
                """
    cursor.execute(sql_str, (ticker_symbol,))
    record = cursor.fetchone()
    return build_from_record(Class, record)

def save(obj, conn, cursor):
    s_str = ', '.join(len(values(obj)) * ['%s'])
    company_str = f"""INSERT INTO {obj.__table__} ({keys(obj)}) VALUES ({s_str});"""
    try:
        cursor.execute(company_str, list(values(obj)))
        conn.commit()
        cursor.execute(f'SELECT * FROM {obj.__table__} ORDER BY id DESC LIMIT 1')
        record = cursor.fetchone()
        return build_from_record(type(obj), record)
    except psycopg2.errors.UniqueViolation as e:
        print(e)
        pass

def values(obj):
    company_attrs = obj.__dict__
    return [company_attrs[attr] for attr in obj.columns if attr in company_attrs.keys()]

def keys(obj):
    company_attrs = obj.__dict__
    selected = [attr for attr in obj.columns if attr in company_attrs.keys()]
    return ', '.join(selected)

def drop_records(cursor, conn, table_name):
    cursor.execute(f"DELETE FROM {table_name};")
    conn.commit()

def drop_tables(table_names, cursor, conn):
    for table_name in table_names:
        drop_records(cursor, conn, table_name)

def drop_all_tables(conn, cursor):
    table_names = ['companies', 'sub_industries', 'quarterly_reports', 'prices_pe']
    drop_tables(table_names, cursor, conn)

def find_by_name(Class, name, cursor):
    query = f"""SELECT * FROM {Class.__table__} WHERE name = %s """
    cursor.execute(query, (name,))
    record =  cursor.fetchone()
    obj = build_from_record(Class, record)
    return obj

def find_or_create_by_name(Class, name, conn, cursor):
    obj = find_by_name(Class, name, cursor)
    if not obj:
        new_obj = Class()
        new_obj.name = name
        obj = save(new_obj, conn, cursor)
    return obj




