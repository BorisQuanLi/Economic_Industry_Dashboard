import pytest
from flask import json
from api.src import create_app
from api.src.db.db import get_db, close_db, drop_records, save
from api.src.models import Company, SubIndustry
from tests.models.helpers.build_records import build_records

@pytest.fixture(scope='module')
def app():
    flask_app = create_app()
    flask_app.config['TESTING'] = True
    flask_app.config['DEBUG'] = True
    return flask_app

@pytest.fixture
def client(app):
    """A test client for the app"""
    return app.test_client()

def test_root_url(app, client):
    response = client.get('/')
    assert b'' in response.data