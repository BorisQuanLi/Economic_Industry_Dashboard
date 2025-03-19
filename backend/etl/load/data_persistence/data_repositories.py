from .base_database_repository import DatabaseRepository
from backend.etl.transform.models.sub_sector.sub_sector import SubSector

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

class SubSectorRepository(DatabaseRepository):
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
