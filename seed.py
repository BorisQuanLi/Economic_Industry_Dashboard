import psycopg2
from api.src import *
import api.src as src
from api.src.db.db import *

drop_all_tables(conn, cursor)

apple = save(src.models.company.Company(
                name= 'Apple Inc', ticker= 'AAPL'),
                conn, cursor)

ibm = save(src.models.company.Company(
                name = 'IBM Corporation', ticker = 'IBM'),
                conn, cursor)

apple_sub_industry = save(src.models.sub_industry.SubIndustry(
                sub_industry_GICS = 'Information Technology',
                sector_GICS = 'Technology Hardware, Storage & Peripherals'),
                conn, cursor)

apple_q4_report = save(src.models.quarterly_report.QuarterlyReport(
                date = '2020-12-01',
                company_id = find_company_id_by_ticker('AAPL', cursor),
                revenue = 1000000,
                cost = 800000,
                net_income = 150000,
                earnings_per_share = 1.23),
                conn, cursor)

ibm_q4_report = save(src.models.quarterly_report.QuarterlyReport(
                date = '2020-12-01',
                company_id = find_company_id_by_ticker('IBM', cursor),
                revenue = 900000,
                cost = 8200000,
                net_income = 140000,
                earnings_per_share = 1.11),
                conn, cursor)

apple_q3_report = save(src.models.quarterly_report.QuarterlyReport(
                date = '2020-09-01',
                company_id = find_company_id_by_ticker('AAPL', cursor),
                revenue = 1100000,
                cost = 850000,
                net_income = 160000,
                earnings_per_share = 1.33),
                conn, cursor)

apple_1226_price = save(src.models.price_pe.PricePE(
                date = '2020-12-26',
                company_id = find_company_id_by_ticker('AAPL', cursor),
                closing_price = 88.63),
                conn, cursor)
                # price-earnings_ratio?
"""
def build_city_state(city_name = '', state_name = ''):
    state = find_or_create_by_name(src.State, state_name, conn, cursor)
    city = find_by_name(src.City, city_name, cursor)
    if not city:
        city = City(name = state_name, state_id = state.id)
        save(city, conn, cursor)
    return city, state

manhattan, new_york = build_city_state('Manhattan', 'New York')
brooklyn, new_york = build_city_state('Brooklyn', 'New York')
philadelphia, pennsylvania = build_city_state('Philadelphia', 'Pennsylvania')

south_philly_zip = save(Zipcode(code=19019, city_id = philadelphia.id), conn, cursor)
chelsea_zip = save(Zipcode(code=10001, city_id = manhattan.id), conn, cursor)
dumbo_zip = save(Zipcode(code=11210, city_id = brooklyn.id), conn, cursor)

los_tacos = save(Venue(name='Los Tacos Al Pastor', price = 1), conn, cursor)
location = save(Location(longitude = 40.7024 , latitude = -73.9875,
        address='141 Front Street', zipcode_id = dumbo_zip.id, venue_id = los_tacos.id), conn, cursor)


grimaldis = save(Venue(foursquare_id = '1234', name = 'Grimaldis', price = 2,
        rating = 2, likes = 3, menu_url = 'grimaldis.com'), conn, cursor)
save(Location(longitude = 40.7024 , latitude = -73.9875,
        address='1 Front Street', zipcode_id = dumbo_zip.id, venue_id = grimaldis.id), conn, cursor)

mogador = save(Venue(foursquare_id = '9923', name = 'Cafe Mogador', 
        price = 3, rating = 4, likes = 15, menu_url = 'cafemogador.com'), conn, cursor)

save(Location(longitude = 40.7024 , latitude = -73.9875,
        address='133 Wythe Avenue', zipcode_id = chelsea_zip.id, venue_id = mogador.id), conn, cursor)

zahav = save(Venue(foursquare_id = '9912', name = 'Zahavs',
        price = 4, rating = 5, likes = 100, menu_url = 'zahavs.com'), conn, cursor)

save(Location(longitude = 40.7024 , latitude = -73.9875,
        address='237 James Street', zipcode_id = south_philly_zip.id, venue_id = zahav.id), conn, cursor)

pizza = save(Category(name = 'Pizza'), conn, cursor)
italian = save(Category(name = 'Italian'), conn, cursor)
bar = save(Category(name = 'Bar'), conn, cursor)
mediterranean = save(Category(name = 'mediterranean'), conn, cursor)

save(VenueCategory(venue_id = grimaldis.id, category_id = pizza.id), conn, cursor)
save(VenueCategory(venue_id = grimaldis.id, category_id = italian.id), conn, cursor)

save(VenueCategory(venue_id = mogador.id, category_id = italian.id), conn, cursor)
save(VenueCategory(venue_id = mogador.id, category_id = bar.id), conn, cursor)


save(VenueCategory(venue_id = zahav.id, category_id = mediterranean.id), conn, cursor)
save(VenueCategory(venue_id = zahav.id, category_id = bar.id), conn, cursor)


"""