"""Sector model for industry analysis."""

class Sector:
    """Model representing a sector."""

    def __init__(self, id=None, name=None, gics_code=None, description=None, sector_gics=None, sector_name=None):
        """Initialize a Sector instance."""
        self.id = id
        self.name = name if name else sector_name
        self.gics_code = gics_code if gics_code else sector_gics
        self.description = description

    @classmethod
    def find_by_id(cls, sector_id, cursor):
        """
        Find a sector by ID.

        Args:
            sector_id (int): The sector ID
            cursor: Database cursor

        Returns:
            Sector: The sector if found, None otherwise
        """
        cursor.execute("SELECT * FROM sectors WHERE id = %s", (sector_id,))
        record = cursor.fetchone()
        if record:
            return cls(
                id=record.get('id'),
                name=record.get('name', record.get('sector_name')),
                gics_code=record.get('gics_code', record.get('sector_gics')),
                description=record.get('description')
            )
        return None

    @classmethod
    def find_all(cls, cursor):
        """
        Find all sectors.

        Args:
            cursor: Database cursor

        Returns:
            list: List of Sector objects
        """
        cursor.execute("SELECT * FROM sectors")
        return [cls(
            id=row['id'],
            name=row['name'],
            gics_code=row['gics_code'],
            description=row.get('description')
        ) for row in cursor.fetchall()]
