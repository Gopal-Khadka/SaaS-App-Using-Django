import datetime
import time


def timestamp_as_datetime(timestamp):
    """Converts timestamp into Python datetime object"""
    return datetime.datetime.fromtimestamp(timestamp, tz=datetime.UTC)
