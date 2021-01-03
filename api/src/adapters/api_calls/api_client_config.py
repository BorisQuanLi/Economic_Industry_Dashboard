import intrinio_sdk as intrinio
from intrinio_sdk.rest import ApiException

# Intrinio API key:
intrinio_api_key = 'OjJhOWFhM2YxODBlMjU3NDgzZDdjOTAyMTUwZDBlNWNm'

# As in:
#intrinio.ApiClient().set_api_key(api_key)
intrinio.ApiClient().allow_retries(True)

# finnhub.io API key:
finnhub_api_key = 'bvebbjn48v6oh223ad00'
finnhub_sandbox_api_key = 'sandbox_bvebbjn48v6oh223ad0g'