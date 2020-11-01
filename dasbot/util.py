from datetime import datetime
from datetime import timedelta
from datetime import timezone


def next_noon(now):
    base_date = now.date()
    if now.hour >= 12:
        base_date = now.date() + timedelta(days=1)

    return datetime(
        year=base_date.year,
        month=base_date.month,
        day=base_date.day,
        hour=12,
        tzinfo=timezone.utc
    )
