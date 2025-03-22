from .base_database_repository import DatabaseRepository
from backend.etl.transform.models.industry.subindustry_model import SubIndustry  # Updated import

class CompanyRepository(DatabaseRepository):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def save(self, data):
        # Implementation
        pass

    def get(self, query):
        # Implementation
        pass

    def delete(self, query):
        # Implementation
        pass

class SectorRepository(DatabaseRepository):
    def __init__(self, db_connection):
        self.db_connection = db_connection

    def save(self, data):
        # Implementation
        pass

    def get(self, query):
        # Implementation
        pass

    def delete(self, query):
        # Implementation
        pass

class SubIndustryRepository(DatabaseRepository):
    def __init__(self, db_connection):
        self.db_connection = db_connection
    
    def save(self, data):
        # Implementation
        pass

    def get(self, query):
        # Implementation  
        pass

    def delete(self, query):
        # Implementation
        pass
