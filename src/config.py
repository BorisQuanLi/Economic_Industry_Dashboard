import intrinio_sdk as intrinio
from intrinio_sdk.rest import ApiException

# Intrinio API key:
api_key = 'OjJhOWFhM2YxODBlMjU3NDgzZDdjOTAyMTUwZDBlNWNm'

intrinio.ApiClient().set_api_key(api_key)
intrinio.ApiClient().allow_retries(True)

api_client = intrinio