"""Calendar-month arithmetic on datetime.date values."""

import calendar
import datetime


def ensure_date(value, name):
    if type(value) is not datetime.date:
        raise TypeError(f"{name} must be a datetime.date")


def ensure_int(value, name):
    if not isinstance(value, int) or isinstance(value, bool):
        raise TypeError(f"{name} must be an int")


def last_day(year, month):
    ensure_int(year, "year")
    ensure_int(month, "month")
    if not 1 <= year <= 9999 or not 1 <= month <= 12:
        raise ValueError("year or month out of range")
    return datetime.date(year, month, calendar.monthrange(year, month)[1])


def add_months(day, n):
    ensure_date(day, "day")
    ensure_int(n, "n")
    year, month0 = divmod(day.year * 12 + day.month - 1 + n, 12)
    if not 1 <= year <= 9999:
        raise ValueError("resulting year out of range")
    month = month0 + 1
    return datetime.date(year, month, min(day.day, last_day(year, month).day))


def whole_months_between(start, end):
    ensure_date(start, "start")
    ensure_date(end, "end")
    if start > end:
        raise ValueError("start must not be later than end")
    months = (end.year - start.year) * 12 + end.month - start.month
    if end.day < start.day:
        months -= 1
    return months
