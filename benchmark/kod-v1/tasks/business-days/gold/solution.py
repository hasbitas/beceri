"""Business-day counting with validated calendar dates."""
import re
from datetime import date, timedelta


def _parse(value):
    if not isinstance(value, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        raise ValueError("expected YYYY-MM-DD")
    return date.fromisoformat(value)


def business_days(start, end, holidays):
    first, stop = _parse(start), _parse(end)
    if first > stop:
        raise ValueError("start is later than end")
    excluded = {_parse(value) for value in holidays}
    weeks, remainder = divmod((stop - first).days, 7)
    total = weeks * 5
    total += sum((first.weekday() + offset) % 7 < 5 for offset in range(remainder))
    return total - sum(first <= day < stop and day.weekday() < 5 for day in excluded)
