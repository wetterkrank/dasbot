from datetime import datetime
from datetime import timedelta
from datetime import timezone
from datetime import time


def next_noon(now):
    """
    :param now: timestamp when the function is called
    :return: the nearest noon datetime
    """
    base_date = now.date()
    if now.hour >= 12:
        base_date = now.date() + timedelta(days=1)
    return datetime(
        year=base_date.year,
        month=base_date.month,
        day=base_date.day,
        hour=12,
        tzinfo=now.tzinfo
    )


def next_quiz_time(last_quiz_time, now=None):
    """
    :param last_quiz_time: the previous time quiz was scheduled
    :param now: timestamp when the function is called
    :return: same time + 1 day (i.e. tomorrow)
    """
    if now is None:
        now = datetime.now(tz=timezone.utc)
    tomorrow_date = now.date() + timedelta(days=1)
    return last_quiz_time.replace(year=tomorrow_date.year,
                                  month=tomorrow_date.month,
                                  day=tomorrow_date.day)


def utc_to_local(hhmm):
    """ Returns the HH:MM time converted from UTC to server's TZ """
    utc = datetime.strptime(f"{hhmm}UTC", "%H:%M%Z")
    now = time.time()
    offset = datetime.fromtimestamp(now) - datetime.utcfromtimestamp(now)
    local = utc + offset
    return datetime.strftime(local, "%H:%M")
