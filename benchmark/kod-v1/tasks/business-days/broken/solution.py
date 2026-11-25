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
    excluded = [_parse(value) for value in holidays]
    total = 0
    for ordinal in range(first.toordinal(), stop.toordinal() + 1):
        if date.fromordinal(ordinal).weekday() < 5:
            total += 1
    for holiday in excluded:
        if first <= holiday <= stop and holiday.weekday() < 5:
            total -= 1
    return total
