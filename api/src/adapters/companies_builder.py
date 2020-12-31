import api.src.models as models
import api.src.db as db
import api.src.adapters as adapters
import psycopg2

import api.src.models

class Builder:
    def run(self, venue_details, conn, cursor):
        venue = VenueBuilder().run(venue_details, conn, cursor)
        if venue.exists:
            return {'venue': venue, 'location': venue.location(cursor), 
                    'venue_categories': venue.venue_categories(cursor)}
        else:
            location = LocationBuilder().run(venue_details, venue, conn, cursor)
            venue_categories = CategoryBuilder().run(venue_details, venue, conn, cursor)
            return {'venue': venue, 'location': location, 'venue_categories': venue_categories}

class SubIndustryBuilder:
    attributes = ['sub_industry_GICS', 'sector_GICS']
    
    def select_attributes(self, sub_industry_details):
        """
        sub_industry_details: a dictionary
        """
        sub_industry = sub_industry_details['sub_industry_GICS']
        sector = sub_industry_details['sector_GICS']
        return dict(zip(self.attributes, [sub_industry, sector]))

    def run(self, sub_industry_details, conn, cursor):
        selected = self.select_attributes(sub_industry_details)
        sub_industry = db.save(models.SubIndustry(**selected),conn, cursor)
        return sub_industry

cool_stuff_sub_industry = SubIndustryBuilder()
cool_stuff_sub_industry.run({'sub_industry_GICS': 'cool stuff', 'sector_GICS': 'IT'},
                            db.conn, db.cursor)


class CompanyBuilder:
    attributes = ['id', 'name', 'ticker', 'sub_industry_id', 'number_of_employees', 
                    'HQs_state', 'country', 'year_founded']
    
    def select_attributes(self, company_details):
        menu_url = venue_details.get('delivery', '')
        if menu_url:
            menu_url = menu_url.get('url', '').split('?')[0]
        foursquare_id, name, price, rating = venue_details['id'], venue_details['name'], venue_details.get('price', {}).get('tier', None), venue_details.get('rating', None)
        likes = venue_details.get('likes', {}).get('count', None)
        return dict(zip(self.attributes, [foursquare_id, name, price, rating, likes, menu_url]))

    def run(self, venue_details, conn, cursor):
        selected = self.select_attributes(venue_details)
        foursquare_id = selected['foursquare_id']
        venue = models.Venue.find_by_foursquare_id(foursquare_id, cursor)
        if venue:
            venue.exists = True
            return venue
        else:
            venue = db.save(models.Venue(**selected), conn, cursor)
            venue.exists = False
            return venue

class LocationBuilder:
    attributes = ['lng', 'lat', 'address', 'postalCode',
            'city', 'state']
    def select_attributes(self, venue_details):
        location = venue_details['location']
        reduced_dict = {k:v for k,v in location.items() if k in self.attributes}
        return reduced_dict

    def run(self, venue_details, venue, conn, cursor):
        location_attributes = self.select_attributes(venue_details)
        location = self.build_location_city_state_zip(location_attributes, conn, cursor)
        location.venue_id = venue.id
        location = db.save(location, conn, cursor)
        return location

    def find_or_create_by_city_state_zip(self, city_name = 'N/A', state_name = 'N/A', code = None, conn = None, cursor = None):
        if not city_name or not state_name: raise KeyError('must provide conn or cursor')
        state = db.find_or_create_by_name(models.State, state_name, conn, cursor)
        city = db.find_by_name(models.City, city_name, cursor)
        zipcode = models.Zipcode.find_by_code(code, cursor)
        if not city:
            city = models.City(name = city_name, state_id = state.id)
            city = db.save(city, conn, cursor)
        if not zipcode:
            zipcode = models.Zipcode(code = code, city_id = city.id)
            zipcode = db.save(zipcode, conn, cursor)
        return city, state, zipcode

    def build_location_city_state_zip(self, location_attr, conn, cursor):
        city_name = location_attr.pop('city', 'N/A')
        state_name = location_attr.pop('state', 'N/A')
        code = location_attr.pop('postalCode', None)
        city, state, zipcode = self.find_or_create_by_city_state_zip(city_name, state_name, code, conn, cursor)
        location = models.Location(latitude = location_attr.get('lat', None),
                longitude = location_attr.get('lng', None),
                address = location_attr.get('address', ''),
                zipcode_id = zipcode.id
                )
        return location

class CategoryBuilder:
    def select_attributes(self, venue_details):
        categories = [category['name'] for category in venue_details['categories']]
        return categories

    def find_or_create_categories(self, category_names, conn, cursor):
        if not isinstance(category_names, list): raise TypeError('category_names must be list')
        categories = []
        for name in category_names:
            category = db.find_or_create_by_name(models.Category, 
                name, conn, cursor)
            categories.append(category)
        return categories

    def create_venue_categories(self, venue, categories, conn, cursor):
        categories = [models.VenueCategory(venue_id = venue.id, category_id = category.id)
                for category in categories]
        return [db.save(category, conn, cursor) for category in categories]

    def run(self, venue_details, venue, conn, cursor):
        category_names = self.select_attributes(venue_details)
        categories = self.find_or_create_categories(category_names, conn, cursor)
        venue_categories = self.create_venue_categories(venue, categories, conn, cursor)
        return venue_categories





