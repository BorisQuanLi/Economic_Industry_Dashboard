import pytest
from flask import json
from api.src import create_app
from api.src.db.db import get_db, close_db, drop_records, save
from api.src.models import Venue, Category

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


def build_records(conn, cursor):

    famiglia = Venue(foursquare_id = '1234', name = 'La Famiglia', price = 1,
            rating = 2, likes = 3, menu_url = 'lafamig.com')
    mogador = Venue(foursquare_id = '5678', name = 'Cafe Mogador', 
            price = 3, rating = 4, likes = 15, menu_url = 'cafemogador.com')
    save(famiglia, conn, cursor)
    save(mogador, conn, cursor)
    pizza = Category(name = 'Pizza')
    italian = Category(name = 'Italian')
    save(pizza, conn, cursor)
    save(italian, conn, cursor)

@pytest.fixture
def client(app):
    """A test client for the app."""
    return app.test_client()

def test_root_url(app, client):
    response = client.get('/')
    assert b'Welcome to the foursquare api' in response.data

def test_restaurants_index(app, client):
    response = client.get('/venues')
    json_response = json.loads(response.data)

    assert len(json_response) == 2
    assert json_response[0]['name'] == 'La Famiglia'
    assert json_response[1]['name'] == 'Cafe Mogador'
    assert list(json_response[0].keys()) == ['id', 'foursquare_id', 'name', 'price', 'rating', 'likes', 'menu_url']

def test_restaurants_show(app, client):
    response = client.get('/venues')
    json_response = json.loads(response.data)
    last_record_id = json_response[-1]['id']

    response = client.get(f'/venues/{last_record_id}')
    json_response = json.loads(response.data)
    assert json_response['name'] == 'Cafe Mogador'

