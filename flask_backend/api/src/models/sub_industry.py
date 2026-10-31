# Re-export the full SubIndustry implementation from etl_service.
# The flask_backend routes use api.src.models.SubIndustry; this keeps the import
# path correct while avoiding code duplication.
from etl_service.src.models.sub_industry import SubIndustry

__all__ = ['SubIndustry']
