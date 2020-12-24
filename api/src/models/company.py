

class Company:
    __table__ = "companies"
    columns = ['id', 'name', 'ticker', 'sub_industry_id', 'number_of_employees', 'HQs_state', 'country', 'year_founded']

    def __init__(self, **kwargs):
        for key in kwargs.keys():
            if key not in self.columns:
                raise f'{key} not in {self.columns}'
        for k, v in kwargs.items():
            setattr(self, k, v)

    @classmethod
    def find_by_name(self, name, cursor):
        company_query_str = """SELECT * FROM companies
                                WHERE company_name = %s;"""
        cursor.execute(company_query_str, (name,))
        company_record = cursor.fetchone()
        company = db.build_from_record(self, company_record)
        return company

    @classmethod
    def find_or_create_by_name(self, name, conn, cursor):
        company = self.find_by_name(name)
        if not company:
            new_company = models.Company()
            new_company.company_name = name
            db.save(new_company, conn, cursor)
            company = self.find_by_name(name, cursor)
        return company

    @classmethod
    def find_by_stock_ticker(self, stock_ticker, cursor):
        ticker_query = """SELECT * FROM companies WHERE stock_ticker = %s;"""
        cursor.execute(ticker_query, (stock_ticker,))
        company_record = cursor.fetchone()
        return db.build_from_record(models.Company, company_record)

    def sector(self, cursor):
        sector_query = """SELECT sectors.* FROM company_sectors
        JOIN sectors ON company_sectors.sector_id = sectors.id
        WHERE company_sectors.company_id = %s;"""
        cursor.execute(sector_query, (self.id))
        sector_record = cursor.fetchone()
        return db.build_from_record(models.Sector, sector_record)

    def company_sector(self, cursor):
        query = """SELECT * FROM company_sectors
        JOIN companies ON companies.id = company_sectors.company_id
        WHERE company_sectors.company_id = %s;"""
        cursor.execute(query, (self.id,))
        company_record = cursor.fetchone()
        return db.build_from_record(models.CompanySector, company_record)

    """
    from foursquare-flask-api repo, venue.py

    @classmethod
    def where_str(self, columns):
        column_mapping = {'city': 'cities.name', 'venue': 'venues.name', 
                'city': 'cities.name', 
                'category': 'categories.name', 
                'state': 'states.name', 'zipcode': 'zipcodes.code', 'rating': 'venues.rating', 'price': 'venues.price'}
        mapped_keys = [column_mapping[column] for column in columns]
        return ' = %s AND '.join(mapped_keys)

    

    @classmethod
    def order_by_clause(self, order_by = "", direction = 'DESC'):
        sort_cols = ['price', 'rating', 'likes']
        directions = ['asc', 'desc', '']
        if not order_by: return ""
        elif order_by.lower() not in sort_cols:
            raise KeyError(f'{order_by} not in {sort_cols}')
        elif direction.lower() not in directions:
            raise KeyError(f'{direction} not in {directions}')
        else:
            return f"ORDER BY venues.{order_by} {direction}"

    @classmethod
    def search_clause(self, params):
        order_by = params.pop('order', '')
        direction = params.pop('direction', 'desc')
        where_clause, where_tuple = Venue.where_clause(params)
        order_by_clause = Venue.order_by_clause(order_by, direction)
        combined_clause = where_clause + order_by_clause
        return combined_clause, where_tuple

    @classmethod
    def search(self, params, cursor):
        if not params: return db.find_all(Venue, cursor)
        search_clause, search_tuple = self.search_clause(params)
        cursor.execute(search_clause, search_tuple)
        records = cursor.fetchall()
        return db.build_from_records(Venue, records)

    """