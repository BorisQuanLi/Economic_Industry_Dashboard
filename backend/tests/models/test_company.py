import pytest
from api.src.models import Company, SubIndustry
from api.src.db.db import save, drop_all_tables, get_db, find_all, find, close_db
from api.src import create_app


def build_records(test_conn, test_cursor):
    app_sw_info_tech = save(SubIndustry(**dict(zip(['sub_industry_GICS', 'sector_GICS'],
                                            ['Application Software', 'Information Technology']))), test_conn, test_cursor)
    semiconductor_info_tech = save(SubIndustry(**dict(zip(['sub_industry_GICS', 'sector_GICS'],
                                            ['Semiconductors', 'Information Technology']))), test_conn, test_cursor)
    life_insurance_fin = save(SubIndustry(**dict(zip(['sub_industry_GICS', 'sector_GICS'],
                                            ['Life & Health Insurance', 'Financials']))), test_conn, test_cursor)
    invest_banking_fin = save(SubIndustry(**dict(zip(['sub_industry_GICS', 'sector_GICS'],
                                            ['Investment Banking & Brokerage', 'Financials']))), test_conn, test_cursor)

    # app_sw1 = save(Company(**dict(zip())))

@pytest.fixture()
def db_cursor():
    flask_app = create_app(database='investment_analysis_test', testing = True, debug = True)

    with flask_app.app_context(): # flask method app_context.  No need to involve .env
        conn = get_db()
        cursor = conn.cursor()

    drop_all_tables(conn, cursor)
    build_records(conn, cursor)
    
    yield cursor
    
    with flask_app.app_context():
        close_db()
        conn = get_db()
        cursor = conn.cursor()
        drop_all_tables(conn, cursor)
        close_db()

def test_venue_location(db_cursor):
    breakpoint() # did not see records written into sub_industries table
    foursquare_id = "4bf58dd8d48988d151941735"
    grimaldis = Venue.find_by_foursquare_id(foursquare_id, db_cursor)
    assert grimaldis.location(db_cursor).address == '1 Front Street'

def test_find_by_foursquare_id(db_cursor):
    foursquare_id = "4bf58dd8d48988d151941735"
    assert Venue.find_by_foursquare_id(foursquare_id, db_cursor).name == 'Grimaldis'

def test_venue_categories(db_cursor):
    foursquare_id = "4bf58dd8d48988d151941735"
    grimaldis = Venue.find_by_foursquare_id(foursquare_id, db_cursor)
    categories = grimaldis.categories(db_cursor)
    category_names = [category.name for category in categories]
    assert category_names == ['Pizza', 'Tourist Spot']

def test_category_search(db_cursor):
    params = {'category': 'Pizza'}
    found_venues = Venue.search(params, db_cursor)
    assert 'Grimaldis' == found_venues[0].name

def test_state_search(db_cursor):
    params = {'state': 'Pennsylvania'}
    found_venues = Venue.search(params, db_cursor)
    assert 'Zahavs' == found_venues[0].name
