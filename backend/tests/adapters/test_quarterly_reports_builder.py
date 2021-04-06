import psycopg2
import pytest
from decimal import *
import api.src.db.db as db
import api.src.models as models
import api.src.adapters as adapters
# from tests.adapters.venue_details import imperfect_venue_details


location =  {'address': '141 Front St', 'crossStreet': 'Pearl St', 'lat': 40.70243624175102, 'lng': -73.98753900608666, 'labeledLatLngs': [{'label': 'display', 'lat': 40.70243624175102, 'lng': -73.98753900608666}], 'postalCode': '11201', 'cc': 'US', 'neighborhood': 'DUMBO', 'city': 'New York', 'state': 'NY', 
        'country': 'United States', 'formattedAddress': ['141 Front St (Pearl St)', 'New York, NY 11201', 'United States']}

categories = [{'id': '4bf58dd8d48988d151941735', 'name': 'Taco Place', 'pluralName': 'Taco Places', 'shortName': 'Tacos', 'icon': {'prefix': 'https://ss3.4sqi.net/img/categories_v2/food/taco_', 'suffix': '.png'}, 'primary': True}]

venue_details = {'id': '5b2932a0f5e9d70039787cf2', 'name': 'Los Tacos Al Pastor', 'categories': categories, 'location': location, 'rating': 7.9, 'price': {'tier': 1}, 'likes': {'count': 52}, 
        'delivery': {'url': 'https://www.seamless.com/menu/los-tacos-al-pastor-141a-front-st-brooklyn/857049?affiliate=1131&utm_source=foursquare-affiliate-network&utm_medium=affiliate&utm_campaign=1131&utm_content=857049'}}

@pytest.fixture()
def test_conn():
    test_conn = psycopg2.connect(dbname = 'foursquare_test', 
            user = 'postgres', password = 'postgres')
    cursor = test_conn.cursor()
    db.drop_all_tables(test_conn, cursor)
    yield test_conn
    db.drop_all_tables(test_conn, cursor)

def test_when_does_not_exist_builds_new_venue_location_and_categories(test_conn):
    test_cursor = test_conn.cursor()
    builder = adapters.Builder()
    venue_objs = builder.run(venue_details, test_conn, test_cursor)
    venue = venue_objs['venue']
    location = venue_objs['location']
    venue_categories = venue_objs['venue_categories']
    zipcode = location.zipcode(test_cursor)
    city = zipcode.city(test_cursor)
    state = city.state(test_cursor)
    assert venue.name == 'Los Tacos Al Pastor'
    assert venue.foursquare_id == '5b2932a0f5e9d70039787cf2'
    assert location.latitude == Decimal('40.70243624175102')
    assert location.longitude == Decimal('-73.98753900608666')
    assert zipcode.code == 11201
    assert city.name == 'New York'
    assert state.name == 'NY'
    assert venue_categories[0].category(test_cursor).name == 'Taco Place'

def test_when_exists_finds_existing_venue_location_and_categories(test_conn):
    test_cursor = test_conn.cursor()
    builder = adapters.Builder()
    venue_objs = builder.run(venue_details, test_conn, test_cursor)
    venue = venue_objs['venue']
    location = venue_objs['location']
    venue_categories = venue_objs['venue_categories']
    zipcode = location.zipcode(test_cursor)
    city = zipcode.city(test_cursor)
    state = city.state(test_cursor)


    new_venue_objs = builder.run(venue_details, test_conn, test_cursor)
    new_venue = new_venue_objs['venue']
    new_location = new_venue_objs['location']
    new_venue_categories = new_venue_objs['venue_categories']
    new_zipcode = location.zipcode(test_cursor)
    new_city = new_zipcode.city(test_cursor)
    new_state = new_city.state(test_cursor)

    assert venue.id == new_venue.id
    assert location.id == new_location.id

    assert city.id == new_city.id
    assert state.id == new_state.id
    assert zipcode.id == new_zipcode.id
    assert location.id == new_location.id
    assert  venue_categories[0].id == new_venue_categories[0].id


def test_when_imperfect_data_exists_builds_new_venue_location_and_categories(test_conn):
    test_cursor = test_conn.cursor()
    builder = adapters.Builder()
    venue_objs = builder.run(imperfect_venue_details, test_conn, test_cursor)
    venue = venue_objs['venue']
    location = venue_objs['location']
    venue_categories = venue_objs['venue_categories']
    zipcode = location.zipcode(test_cursor)
    city = zipcode.city(test_cursor)
    state = city.state(test_cursor)
    assert venue.name == 'Country Boys Tacos'
    assert venue.foursquare_id == '53aefe43498ec970f3cf4aea'
    assert location.latitude == Decimal('40.699322354013994')
    assert location.longitude == Decimal('-73.97475273514199')
    assert zipcode.code == None
    assert city.name == 'Brooklyn'
    assert state.name == 'NY'
    assert venue_categories[0].category(test_cursor).name == 'Food Truck'
