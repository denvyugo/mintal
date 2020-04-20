import datetime as dt
import pytz

TIMEZONE = 'Europe/Moscow'

def daysofmonth(year, month):
    """get quantity of days in month."""
    delta = dt.timedelta(days=1)
    if month == 12:
        new_date = dt.date(year + 1, 1, 1) - delta
    else:
        new_date = dt.date(year, month + 1, 1) - delta
    return new_date.day
        

def datesub_month(monthsub, dateinit=None):
    """"subtraction whole quantity on month from initial date."""
    if dateinit is None:
        dateinit = dt.datetime.today()
    year = dateinit.year
    month = dateinit.month
    day = dateinit.day
    hour = dateinit.hour
    minute = dateinit.minute
    second = dateinit.second
    micro = dateinit.microsecond
    
    if monthsub > 0:
        day_sub = day
        year_sub = year - monthsub // 12
        month_sub = month - monthsub % 12
        if month <= monthsub % 12:
            year_sub -= 1
            month_sub = 12 - (monthsub % 12 - month)
                
        # check if new day within first and last day in month
        days = daysofmonth(year_sub, month_sub)
        if day > days: day_sub = days
        return dt.datetime(year_sub, month_sub, day_sub, hour, minute, second, micro)

def convert_datetime(some_datetime):
    """convert datetime from some format to datetime."""
    dt_return = None
    if isinstance(some_datetime, dt.datetime):
        dt_return = some_datetime
    elif isinstance(some_datetime, int):
        dt_return = dt.datetime.fromtimestamp(some_datetime)
    elif isinstance(some_datetime, str):
        if 'Z' == some_datetime[-1]:
            dt_string = some_datetime[:-1]
            dt_utc = pytz.utc.localize(dt.datetime.fromisoformat(dt_string))
            dt_return = dt_utc.astimezone(pytz.timezone(TIMEZONE))
    else:
        print(some_datetime)
    return dt_return

def local_datetime(some_datetime):
    """localize to timezone."""
    tz = pytz.timezone(TIMEZONE)
    if some_datetime.tzinfo is None:
        dta = tz.localize(some_datetime)
    else:
        dta = some_datetime.astimezone(tz)
    return dta

def local_datetime_string(some_datetime):
    """ make ISO format with local timezone."""
    dta = local_datetime(some_datetime)
    return dta.isoformat(timespec='microseconds')

def format_datetime_string(some_datetime):
    """format datetime to string HH:MM DD-MM-YYYY"""
    return dt.datetime.strftime(some_datetime, '%H:%M %d-%m-%Y')
