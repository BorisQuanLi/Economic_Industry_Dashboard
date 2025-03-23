import warnings
from backend.etl.transform.models.aggregate_analytics.aggregation_by_quarter import QuarterlyPricePE
from backend.etl.load.db.queries.sql_query_strings import company_price_pe_history_query_str
from backend.webservice.database.company_price_pe_service import CompanyPricePEService

warnings.warn(
    "This module is deprecated. Use backend.webservice.services.database.company_price_pe_service instead.",
    DeprecationWarning,
    stacklevel=2
)

class MixinCompanyPricePE:
    """mixin with class Company"""
    def get_all_company_names_in_sub_sector(self, sub_sector_name, cursor):
        warnings.warn(
            "This method is deprecated. Use CompanyPricePEService.get_companies_by_sub_sector instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Delegate to the new service
        service = CompanyPricePEService()
        return service.get_companies_by_sub_sector(sub_sector_name)

    def to_quarterly_price_pe_json(self, company_name, cursor):
        warnings.warn(
            "This method is deprecated. Use CompanyPricePEService.get_quarterly_price_pe instead.",
            DeprecationWarning,
            stacklevel=2
        )
        # Delegate to the new service
        service = CompanyPricePEService()
        return service.get_quarterly_price_pe(company_name)

    def create_price_pe_objs(self, record):
        warnings.warn(
            "This method is deprecated. Use the new service methods instead.",
            DeprecationWarning,
            stacklevel=2
        )
        attr_record_dict = dict(zip(QuarterlyPricePE.attributes, record))
        obj = QuarterlyPricePE(**attr_record_dict)
        return obj.__dict__