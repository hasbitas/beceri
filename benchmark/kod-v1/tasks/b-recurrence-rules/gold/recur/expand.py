"""Expansion of a parsed recurrence rule into concrete dates."""

import calendar
import datetime


def _shift(day, days):
    """Return day moved by a number of days, or None when out of range."""
    try:
        return day + datetime.timedelta(days=days)
    except OverflowError:
        return None


def _daily(rule, start, limit):
    day = start
    while day is not None and day <= limit:
        yield day
        day = _shift(day, rule["interval"])


def _weekly(rule, start, limit):
    weekdays = rule["byday"] or (start.weekday(),)
    monday = _shift(start, -start.weekday())
    while monday is not None and monday <= limit:
        for weekday in weekdays:
            day = _shift(monday, weekday)
            if day is not None and start <= day <= limit:
                yield day
        monday = _shift(monday, 7 * rule["interval"])


def _monthly(rule, start, limit):
    wanted = rule["bymonthday"] or (start.day,)
    index = start.year * 12 + start.month - 1
    while True:
        year, month = divmod(index, 12)
        month += 1
        if year > 9999 or datetime.date(year, month, 1) > limit:
            return
        last = calendar.monthrange(year, month)[1]
        days = set()
        for value in wanted:
            day = last if value == -1 else value
            if day <= last:
                days.add(day)
        for day in sorted(days):
            candidate = datetime.date(year, month, day)
            if start <= candidate <= limit:
                yield candidate
        index += rule["interval"]


_GENERATORS = {"DAILY": _daily, "WEEKLY": _weekly, "MONTHLY": _monthly}


def expand(rule, start, end):
    for name, value in (("start", start), ("end", end)):
        if type(value) is not datetime.date:
            raise TypeError(f"{name} must be a datetime.date")
    limit = end
    if rule["until"] is not None and rule["until"] < limit:
        limit = rule["until"]
    result = []
    for day in _GENERATORS[rule["freq"]](rule, start, limit):
        result.append(day)
        if len(result) == rule["count"]:
            break
    return result
