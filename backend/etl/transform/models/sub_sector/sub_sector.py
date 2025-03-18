"""Sub-sector domain model."""

class SubSector:
    """Represents an industrial sub-sector."""
    
    def __init__(self, name: str, parent_sector: str = None):
        """
        Initialize a sub-sector.
        
        Args:
            name: The name of the sub-sector.
            parent_sector: The broader sector this sub-sector belongs to.
        """
        self.name = name
        self.parent_sector = parent_sector
        self.companies = []
        self.metrics = {}
        
    def add_company(self, company):
        """Add a company to this sub-sector."""
        self.companies.append(company)
        
    def calculate_metrics(self):
        """Calculate aggregate metrics for this sub-sector."""
        # Placeholder for sub-sector specific metrics calculation
        pass
    
    def __repr__(self):
        return f"SubSector({self.name}, sector={self.parent_sector})"
