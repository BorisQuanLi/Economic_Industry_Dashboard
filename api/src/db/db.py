from flask import current_app
from flask import g
import psycopg2

conn = psycopg2.connect(database = 'investment_analysis', user = 'postgres', password = 'postgres')
cursor = conn.cursor()

def get_db():
    if "db" not in g:
        g.db = psycopg2.connect(user = 'postgres', password = 'postgres',
            dbname = current_app.config['DATABASE'])
    return g.db

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

def show_companies_by_sector(Class, sector_name, cursor):
    sql_str = f"""SELECT * FROM companies 
                JOIN sub_industries 
                ON sub_industries.id = companies.sub_industry_id
                WHERE sub_industries.sector_gics = %s;
                """
    cursor.execute(sql_str, (sector_name,))
    records = cursor.fetchall()
    return build_from_records(Class, records)

def find_companies_by_sub_industry(Class, sub_industry_id, cursor):
    """
    param Class: models.Company
    returns Company objects of all the companies in the same sub_industry
    """
    sql_str = f"""SELECT companies.* FROM companies 
                  JOIN sub_industries
                  ON companies.sub_industry_id = sub_industries.id
                  WHERE sub_industries.id = %s;
                """
    cursor.execute(sql_str, (sub_industry_id,))
    records = cursor.fetchall()
    return build_from_records(Class, records)

def find_by_ticker (Class, ticker_symbol, cursor):
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




