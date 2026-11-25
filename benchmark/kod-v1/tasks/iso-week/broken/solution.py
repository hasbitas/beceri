"""Strict Gregorian date to ISO week conversion."""
import datetime
import re


def iso_week(date_text):
    if not isinstance(date_text, str):
        raise TypeError("date_text must be a string")
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", date_text) is None:
        raise ValueError("expected YYYY-MM-DD")
    day = datetime.date(int(date_text[:4]), int(date_text[5:7]), int(date_text[8:]))
    jan4 = datetime.date(day.year, 1, 4)
    first_monday = jan4.toordinal() - jan4.weekday()
    week = (day.toordinal() - first_monday) // 7 + 1
    return (day.year, week)
