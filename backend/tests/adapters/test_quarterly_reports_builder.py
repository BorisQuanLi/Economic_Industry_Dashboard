import pytest
from flask import json
from api.src import create_app
from api.src.db.db import get_db, close_db, drop_records, save
from api.src.models import Company, SubIndustry
from tests.models.helpers.build_records import build_records

# to be modified from test_app.py

@pytest.fixture(scope = 'module')
def app():
    flask_app = create_app('investment_analysis_test', testing = True, debug = True)

    with flask_app.app_context():
        conn = get_db()
        cursor = conn.cursor()
        drop_records(cursor, conn, 'companies')
        drop_records(cursor, conn, 'sub_industries')
        build_records(conn, cursor)
        conn.commit()
        close_db()

    yield flask_app

    with flask_app.app_context():
        close_db()
        conn = get_db()
        cursor = conn.cursor()
        drop_records(cursor, conn, 'companies')
        drop_records(cursor, conn, 'sub_industries')
        close_db()

@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()

def test_root_url(app, client):
    response = client.get('/')
    assert b'' in response.data

