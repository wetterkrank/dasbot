# NOTE: We don't handle TZ changes

from datetime import datetime
from datetime import timedelta
from datetime import timezone

def next_hhmm(hhmm, now):
    """
    :param hhmm: time of the day as a string "HH:MM"
    :param now: datetime when the function is called
    :return: datetime of the next HH:MM, same TZ
    """
    h, m = (int(x) for x in hhmm.split(":"))
    base_date = now.date()
    if now.hour >= h:
        base_date = base_date + timedelta(days=1)
    target = datetime(
        year=base_date.year,
        month=base_date.month,
        day=base_date.day,
        hour=h,
        minute=m,
        tzinfo=now.tzinfo)
    return target


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


def month_ago(now=None):
    """
    :param now: timestamp when the function is called
    :return: same time - 30 days
    """
    if now is None:
        now = datetime.now(tz=timezone.utc)
    month_ago = now - timedelta(days=30)
    return month_ago

def equalizer(n: int, m: int, total: int):
    """
    Receives total, m and n [0..total]
    Returns a tuple (a, b) so that their sum -> total, and a / b -> 1
    """
    oddity = total % 2
    smallest = min(n, m, total // 2 + oddity)
    if smallest == n:
        return (n, min(m, total-n))
    elif smallest == m:
        return (min(n, total-m), m)
    else:
        return (total // 2, total // 2 + oddity)
