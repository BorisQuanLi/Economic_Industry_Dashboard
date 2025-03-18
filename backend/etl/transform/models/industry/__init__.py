"""Industry module imports."""

# Make sure IndustryMetrics is explicitly exported
from .industry_metrics import IndustryMetrics, SectorMetrics, SubSectorMetrics

from .sector import Sector

# Define Industry class if it doesn't exist
class Industry:
    """Represents an industry category."""
    
    def __init__(self, name, sectors=None):
        self.name = name
        self.sectors = sectors or []
        
    def add_sector(self, sector):
        """Add a sector to this industry."""
        self.sectors.append(sector)
        
    def __repr__(self):
        return f"Industry({self.name}, sectors={len(self.sectors)})"

__all__ = ['Industry', 'IndustryMetrics', 'Sector']
