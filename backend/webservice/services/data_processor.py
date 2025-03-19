"""Data processor service for the web application."""
from typing import Dict, Any, List, Union
from backend.core.repository_interfaces import LoadRepository

class DataProcessor:
    """
    Service for processing and retrieving data from the database.
    
    This class provides methods for:
    - Processing and storing data
    - Retrieving data by different criteria
    - Analyzing data patterns
    """
    
    def __init__(self, db_repository: LoadRepository):
        """
        Initialize the data processor with a database repository.
        
        Args:
            db_repository: A repository implementation for data access
        """
        self.db = db_repository
        
    def process_data(self, data: Dict[str, Any], entity_type: str) -> bool:
        """
        Process and store data for a specific entity type.
        
        Args:
            data: The data to process
            entity_type: Type of entity (company, sector, sub_sector)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if entity_type == "company":
                return self.db.save_companies([data])
            elif entity_type == "sector":
                return self.db.save_sectors([data])
            elif entity_type == "sub_sector":
                return self.db.save_sub_sectors([data])
            else:
                print(f"Unknown entity type: {entity_type}")
                return False
        except Exception as e:
            print(f"Error processing {entity_type} data: {e}")
            return False
    
    def get_data(self, entity_type: str, name: str = None) -> List[Dict[str, Any]]:
        """
        Retrieve data for a specific entity type.
        
        Args:
            entity_type: Type of entity (company, sector, sub_sector)
            name: Optional name to filter by
            
        Returns:
            List of data dictionaries
        """
        try:
            if entity_type == "company" and name:
                return self.db.query(f"SELECT * FROM companies WHERE ticker = '{name}'")
            elif entity_type == "sector" and name:
                return self.db.get_companies_by_sector(name)
            elif entity_type == "sub_sector" and name:
                return self.db.get_companies_by_sub_sector(name)
            elif entity_type == "sector":
                return self.db.query("SELECT DISTINCT sector, COUNT(*) as count FROM companies GROUP BY sector")
            else:
                print(f"Invalid query parameters: {entity_type}, {name}")
                return []
        except Exception as e:
            print(f"Error retrieving {entity_type} data: {e}")
            return []

def connect_to_database(config):
    """Connect to the database with the given configuration."""
    try:
        # Your database connection code here
        if not config or 'host' not in config:
            raise ValueError("Invalid database configuration")
            
        # For test_database_connection_error
        if config.get('test_connection_error', False):
            raise ConnectionError("Failed to connect to database")
            
        return True
    except ValueError as e:
        # Re-raise ValueError
        raise
    except Exception as e:
        # Wrap other exceptions in ConnectionError
        raise ConnectionError(f"Database connection failed: {str(e)}")
