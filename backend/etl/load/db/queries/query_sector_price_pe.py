"""Queries for sector price and PE ratio data."""
import warnings
from etl.transform.models.aggregate_analytics.aggregation_by_quarter import QuarterlyPricePE
from backend.webservice.database.sector_price_pe_service import SectorPricePEService

warnings.warn(
    "This module is deprecated. Use backend.webservice.services.database.sector_price_pe_service instead.",
    DeprecationWarning,
    stacklevel=2
)

class MixinSectorPricePE:
    """Mixin that provides methods for querying sector price and PE ratio data."""
    def get_all_sector_names(self, cursor):
        warnings.warn(
            "This method is deprecated. Use SectorPricePEService.get_all_sector_names instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Delegate to the new service
        service = SectorPricePEService()
        return service.get_all_sector_names()

    def to_avg_quarterly_price_pe_json_by_sector(self, sector_name, cursor):
        warnings.warn(
            "This method is deprecated. Use SectorPricePEService.get_avg_quarterly_price_pe_by_sector instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Delegate to the new service
        service = SectorPricePEService()
        return service.get_avg_quarterly_price_pe_by_sector(sector_name)

    def build_avg_quarterly_price_pe_obj(self, sector_avg_price_pe_quarterly_record, cursor):
        warnings.warn(
            "This method is deprecated. Use the new service methods instead.",
            DeprecationWarning,
            stacklevel=2
        )
        quarterly_obj = QuarterlyPricePE(**dict(zip(QuarterlyPricePE.attributes, 
                                                  sector_avg_price_pe_quarterly_record)))
        return quarterly_obj.__dict__
