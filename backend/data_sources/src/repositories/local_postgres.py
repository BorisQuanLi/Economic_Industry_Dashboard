import psycopg2
from typing import Dict, List, Any
from sqlalchemy import create_engine
from .base import DataRepository, DatabaseRepository

class LocalPostgresRepository(DataRepository):
    def __init__(self, connection_params: Dict[str, str]):
        self.conn = psycopg2.connect(**connection_params)
        
    def get_sectors(self) -> List[str]:
        with self.conn.cursor() as cur:
            cur.execute("SELECT DISTINCT sector FROM sectors")
            return [row[0] for row in cur.fetchall()]
            
    def get_sector_metrics(self, sector: str) -> Dict[str, Any]:
        with self.conn.cursor() as cur:
            cur.execute(
                "SELECT revenue, growth FROM sector_metrics WHERE sector = %s",
                (sector,)
            )
            row = cur.fetchone()
            return {"revenue": row[0], "growth": row[1]} if row else {}
            
    def store_raw_data(self, data: Dict[str, Any], dataset_name: str) -> bool:
        try:
            with self.conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO raw_data (dataset_name, data) VALUES (%s, %s)",
                    (dataset_name, data)
                )
                self.conn.commit()
                return True
        except Exception:
            self.conn.rollback()
            return False

class PostgresRepository(DatabaseRepository):
    def _create_engine(self):
        return create_engine(
            f'postgresql://{self.config["username"]}:{self.config["password"]}@'
            f'{self.config["host"]}:{self.config["port"]}/{self.config["database"]}'
        )
