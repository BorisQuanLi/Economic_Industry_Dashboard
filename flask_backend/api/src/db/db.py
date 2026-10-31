"""
Stub db module for flask_backend.
The full implementation lives in etl_service/src/db/db.py.
This file exists so the test conftest.py can patch 'api.src.db.db.get_db'.
"""
import psycopg2


def get_db():
    raise RuntimeError("get_db() must be patched in tests")


def close_db(e=None):
    pass


def drop_records(cursor, conn, table_name):
    cursor.execute(f"DELETE FROM {table_name};")
    conn.commit()


def save(obj, conn, cursor):
    raise RuntimeError("save() must be patched in tests")


def build_from_record(Class, record):
    if not record:
        return None
    attr = dict(zip(Class.columns, record))
    return Class(**attr)


def build_from_records(Class, records):
    return [build_from_record(Class, record) for record in records]
