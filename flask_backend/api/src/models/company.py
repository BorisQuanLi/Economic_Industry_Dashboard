# Re-export the full Company implementation from etl_service.
# The flask_backend routes use api.src.models.Company; this keeps the import
# path correct while avoiding code duplication.
from etl_service.src.models.company import Company

__all__ = ['Company']
