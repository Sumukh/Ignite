import datetime as dt
import pytz

# Timezones. Be cautious with using tzinfo argument. http://pytz.sourceforge.net/
# "tzinfo argument of the standard datetime constructors 'does not work'
# with pytz for many timezones."

def local_time(time, course, fmt='%a %m/%d %I:%M %p'):
    """ Format a time string in a course's locale.
    Note that %-I does not perform as expected on Alpine Linux
    """
    return local_time_obj(time, course).strftime(fmt)

def local_time_obj(time, locale):
    """ Get a Datetime object in a locale from a TZ Aware DT object."""
    if not time.tzinfo:
        time = pytz.utc.localize(time)
    return time.astimezone(locale)

def server_time_obj(time, locale):
    """ Convert a datetime object from a locale to a UTC
    datetime object.
    """
    if not time.tzinfo:
        time = locale.localize(time)
    # Store using UTC on the server side.
    return time.astimezone(pytz.utc)

def future_time_obj(locale, **kwargs):
    """ Get a datetime object representing some timedelta from now with the time
    set at 23:59:59.
    """
    date = locale.localize(dt.datetime.now() + dt.timedelta(**kwargs))
    time = dt.time(hour=23, minute=59, second=59, microsecond=0)
    return dt.datetime.combine(date, time)
