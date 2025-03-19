from typing import Dict, List, Any

class IndustryAnalyzer:
    def __init__(self, db_manager=None):
        self.db_manager = db_manager

    def get_sector_breakdown(self) -> Dict[str, Any]:
        """Get breakdown of companies by sector"""
        if not self.db_manager:
            return {}
        return self.db_manager.execute_query("SELECT sector, COUNT(*) FROM companies GROUP BY sector")

    def get_sector_metrics(self, sector: str) -> Dict[str, Any]:
        """Get metrics for a specific sector"""
        if not self.db_manager:
            return {}
        return self.db_manager.execute_query(
            "SELECT AVG(price) as avg_price, COUNT(*) as company_count FROM companies WHERE sector = %s",
            (sector,)
        )

    def get_subsector_companies(self, subsector: str) -> List[Dict[str, Any]]:
        """Get companies in a specific subsector"""
        if not self.db_manager:
            return []
        return self.db_manager.execute_query(
            "SELECT * FROM companies WHERE subsector = %s",
            (subsector,)
        )

    def get_subsector_metrics(self, subsector: str) -> Dict[str, Any]:
        """Get metrics for a specific subsector"""
        if not self.db_manager:
            return {}
        return self.db_manager.execute_query(
            "SELECT AVG(price) as avg_price, COUNT(*) as company_count FROM companies WHERE subsector = %s",
            (subsector,)
        )

    def save_sector_data(self, data: Dict[str, Any]) -> bool:
        """Save sector data to database"""
        if not self.db_manager:
            return False
        try:
            self.db_manager.execute_query(
                "INSERT INTO sector_data (sector_name, metrics) VALUES (%s, %s)",
                (data['sector'], data['metrics'])
            )
            return True
        except Exception:
            return False
