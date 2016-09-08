from datetime import datetime, time, date


def to_ts(dt):
    """
    This function converts datetime or time object to Unix timestamp (the number of seconds from now to 1970/01/01 00:00:00)
    :param dt: datetime / time object
    :return: Unix timestamp
    """
    if type(dt) == time:
        dt = datetime.combine(date(1970, 1, 1), dt)
    delta = dt - datetime(1970, 1, 1, 0, 0, 0)
    return int(delta.total_seconds())


def to_dt(ts):
    """
    This function converts Unix timestamp to datetime object
    :param ts: timestamp
    :return: the datetime object
    """
    return datetime.utcfromtimestamp(ts)


def extract_hour_dt(dt):
    """
    This function gets the hour of the datetime object
    :param dt: the datetime object
    :return: the datetime object
    """
    return dt.replace(minute=0, second=0, microsecond=0)


def extract_date(dt):
    """
    This function gets the date from the datetime object
    :param dt: the datetime object
    :return: the datetime object
    """
    return dt.date()


# add auth controll
def admin_auth():
    return True


def user_auth():
    return True


def merchant_auth():
    return True


def maintainer_auth():
    return True
