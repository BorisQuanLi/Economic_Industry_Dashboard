"""Sub-industry model for detailed industry classification."""
from dataclasses import dataclass
from typing import Optional

@dataclass
class SubIndustry:
    """Model representing a sub-industry."""
    
    def __init__(self, id=None, sub_industry_gics=None, sector_id=None, sector_gics=None):
        """Initialize a SubIndustry instance."""
        self.id = id
        self.sub_industry_gics = sub_industry_gics
        self.sector_id = sector_id
        self.sector_gics = sector_gics

    @classmethod
    def find_by_sector(cls, sector_gics: str, cursor) -> list['SubIndustry']:
        """Get all sub-industries in a sector."""
        cursor.execute("""
            SELECT id, sub_industry_name, sub_industry_gics, 
                   sector_gics, description
            FROM sub_industries 
            WHERE sector_gics = %s
            ORDER BY sub_industry_name
        """, (sector_gics,))
        return [cls(
            id=row[0],
            name=row[1],
            sub_industry_gics=row[2],
            sector_gics=row[3],
            description=row[4]
        ) for row in cursor.fetchall()]
