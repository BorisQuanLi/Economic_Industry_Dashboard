import psycopg2
import pandas as pd
from backend.common.repositories import LoadRepository

class LocalPostgresRepository(LoadRepository):
    """Repository for PostgreSQL database operations"""
    
    def __init__(self, connection_string=None, **kwargs):
        """
        Initialize the repository with connection parameters
        
        Args:
            connection_string: PostgreSQL connection string in the format
                               postgresql://user:password@host:port/dbname
            **kwargs: Alternative connection parameters (db_name, username, password, port)
        """
        self.connection_string = connection_string
        self.connection_params = kwargs
        self.connection = None
        self.cursor = None
    
    def connect(self):
        """Establish connection to the database"""
        try:
            if self.connection_string:
                self.connection = psycopg2.connect(self.connection_string)
            else:
                # Use individual parameters if no connection string provided
                self.connection = psycopg2.connect(**self.connection_params)
            
            self.cursor = self.connection.cursor()
            return True
        except Exception as e:
            print(f"Error connecting to PostgreSQL: {e}")
            return False
    
    def is_connected(self):
        """Check if connection is established"""
        return self.connection is not None and self.cursor is not None
    
    def save_dataframe(self, df, table_name):
        """Save DataFrame to database table"""
        if not self.is_connected():
            self.connect()
            
        try:
            # Implementation for saving dataframe to postgres table
            # (simplified for this example)
            self.connection.commit()
            return True
        except Exception as e:
            print(f"Error saving data: {e}")
            return False
    
    def query(self, query_string):
        """Execute query and return results as DataFrame"""
        if not self.is_connected():
            self.connect()
            
        try:
            self.cursor.execute(query_string)
            results = self.cursor.fetchall()
            
            # Get column names from cursor description
            columns = [desc[0] for desc in self.cursor.description]
            
            # Create DataFrame from results
            return pd.DataFrame(results, columns=columns)
        except Exception as e:
            print(f"Error executing query: {e}")
            return pd.DataFrame()
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None
            self.cursor = None
    
    # Implement LoadRepository methods
    def save_companies(self, companies):
        """Save company data to PostgreSQL."""
        if not companies:
            return False
            
        if not self.is_connected():
            self.connect()
            
        # Convert list of dicts to DataFrame
        df = pd.DataFrame(companies)
        return self.save_dataframe(df, 'companies')
    
    def save_sectors(self, sectors):
        """Save sector data to PostgreSQL."""
        if not sectors:
            return False
            
        if not self.is_connected():
            self.connect()
            
        # Convert list of dicts to DataFrame
        df = pd.DataFrame(sectors)
        return self.save_dataframe(df, 'sectors')
    
    def save_sub_sectors(self, sub_sectors):
        """Save sub-sector data to PostgreSQL."""
        if not sub_sectors:
            return False
            
        if not self.is_connected():
            self.connect()
            
        # Convert list of dicts to DataFrame
        df = pd.DataFrame(sub_sectors)
        return self.save_dataframe(df, 'sub_sectors')
    
    def save_metrics(self, entity_type, entity_id, metrics):
        """Save metrics for a specific entity to PostgreSQL."""
        if not metrics:
            return False
            
        if not self.is_connected():
            self.connect()
            
        # Flatten metrics and add entity identifiers
        flat_metrics = {**metrics, 'entity_type': entity_type, 'entity_id': entity_id}
        df = pd.DataFrame([flat_metrics])
        return self.save_dataframe(df, f'{entity_type}_metrics')

class PostgresRepository(DatabaseRepository):
    def _create_engine(self):
        return create_engine(
            f'postgresql://{self.config["username"]}:{self.config["password"]}@'
            f'{self.config["host"]}:{self.config["port"]}/{self.config["database"]}'
        )
