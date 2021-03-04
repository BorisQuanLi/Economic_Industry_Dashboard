import intrinio_sdk as intrinio
from intrinio_sdk.rest import ApiException
import finnhub
import datetime
import pytz

"""
https://www.kite.com/python/answers/how-to-get-the-most-recent-previous-business-day-in-python
"""

def most_recent_busines_day_eastern(today = datetime.datetime.today()):
    """returns the most recent business day in the U.S. Eastern time zone."""
    # convert passed-in argument "today" to the Eastern Standard Time
    today = today.astimezone(pytz.timezone('US/Eastern')).date()
    offset = max(1, (today.weekday() + 6) % 7 - 3)  # Equation to find time elapsed
    timedelta = datetime.timedelta(offset)
    most_recent_est = today - timedelta
    return most_recent_est

def most_recent_busines_day(today = datetime.datetime.today().date()):
    """
    named argument 'today' is based on the operating system's local time zone.
    """
    # Equation to find time elapsed
    offset = max(1, (today.weekday() + 6) % 7 - 3)  
    timedelta = datetime.timedelta(offset)
    most_recent = today - timedelta
    return most_recent

def activate_intrinio_api():
    intrinio.ApiClient().set_api_key('OjJhOWFhM2YxODBlMjU3NDgzZDdjOTAyMTUwZDBlNWNm')
    intrinio.ApiClient().allow_retries(True)
    
def finnhub_client():
    api_key = 'bvebbjn48v6oh223ad00'
    sandbox_api_key = 'sandbox_bvebbjn48v6oh223ad0g'
    # Setup client
    finnhub_client = finnhub.Client(api_key= api_key)
    return finnhub_client

def date_to_datetime(datetime_date):
    """ converts a datetime.date to datetime.datime object"""
    return datetime.datetime(datetime_date.year,
                             datetime_date.month,
                             datetime_date.day)

def datetime_to_unix_time(dt):
    """
    parameter: Python datetime object, such as datetime.datetime(2015, 10, 19).
    
    returns the corrsonding UTC in integer (down to the second), in 
    accordance with the finnhub.Client() methods' parameter data type
    
    Need to first import pytz
    https://www.programiz.com/python-programming/datetime/timestamp-datetime
    """
    if type(dt) == datetime.date:
        dt = date_to_datetime(dt)
    return int(datetime.datetime.timestamp(dt))

def unix_time_to_datetime_eastern(unix_time_int):
    """converts Unix time to Python datetime.datetime object in 
    the U.S. Eastern time zone."""
    os_timezone_datetime = datetime.datetime.fromtimestamp(unix_time_int)
    eastern = pytz.timezone('US/Eastern')
    return os_timezone_datetime.astimezone(eastern)

def day_of_year(date_string):
    """
    date_string format: yyyy-mm-dd
    """
    date_datetime = datetime.datetime.strptime(date_string, '%Y-%m-%d')
    return int(date_datetime.timetuple().tm_yday)

    
    