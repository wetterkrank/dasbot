from datetime import timedelta


def next_noon(now):
    return (now + timedelta(days=1)).replace(hour=12, minute=0, second=0, microsecond=0)
