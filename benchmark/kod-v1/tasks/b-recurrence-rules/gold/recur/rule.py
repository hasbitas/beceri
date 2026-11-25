"""Parsing of recurrence rule strings such as 'FREQ=WEEKLY;BYDAY=MO,WE'."""

import datetime

WEEKDAYS = {"MO": 0, "TU": 1, "WE": 2, "TH": 3, "FR": 4, "SA": 5, "SU": 6}
FREQUENCIES = ("DAILY", "WEEKLY", "MONTHLY")
KEYS = ("FREQ", "INTERVAL", "BYDAY", "BYMONTHDAY", "COUNT", "UNTIL")


def _positive_int(text, name):
    if not (text.isascii() and text.isdigit()) or int(text) < 1:
        raise ValueError(f"{name} must be a positive integer")
    return int(text)


def _parse_byday(text):
    seen = set()
    for token in text.split(","):
        if token not in WEEKDAYS:
            raise ValueError(f"unknown weekday {token!r}")
        seen.add(WEEKDAYS[token])
    return tuple(sorted(seen))


def _parse_bymonthday(text):
    seen = set()
    for token in text.split(","):
        if token == "-1":
            seen.add(-1)
            continue
        day = _positive_int(token, "BYMONTHDAY")
        if day > 31:
            raise ValueError("BYMONTHDAY must be between 1 and 31 or -1")
        seen.add(day)
    return tuple(sorted(seen))


def _parse_until(text):
    if len(text) != 8 or not (text.isascii() and text.isdigit()):
        raise ValueError("UNTIL must have the form YYYYMMDD")
    return datetime.date(int(text[:4]), int(text[4:6]), int(text[6:]))


def parse_rule(text):
    if not isinstance(text, str):
        raise TypeError("rule must be a string")
    fields = {}
    for part in text.split(";"):
        key, sep, value = part.partition("=")
        if not sep or not value:
            raise ValueError(f"malformed part {part!r}")
        if key not in KEYS:
            raise ValueError(f"unknown key {key!r}")
        if key in fields:
            raise ValueError(f"duplicate key {key!r}")
        fields[key] = value
    if "FREQ" not in fields:
        raise ValueError("FREQ is required")
    freq = fields["FREQ"]
    if freq not in FREQUENCIES:
        raise ValueError(f"unknown frequency {freq!r}")
    if "BYDAY" in fields and freq != "WEEKLY":
        raise ValueError("BYDAY requires FREQ=WEEKLY")
    if "BYMONTHDAY" in fields and freq != "MONTHLY":
        raise ValueError("BYMONTHDAY requires FREQ=MONTHLY")
    if "COUNT" in fields and "UNTIL" in fields:
        raise ValueError("COUNT and UNTIL are mutually exclusive")
    return {
        "freq": freq,
        "interval": _positive_int(fields["INTERVAL"], "INTERVAL") if "INTERVAL" in fields else 1,
        "byday": _parse_byday(fields["BYDAY"]) if "BYDAY" in fields else (),
        "bymonthday": _parse_bymonthday(fields["BYMONTHDAY"]) if "BYMONTHDAY" in fields else (),
        "count": _positive_int(fields["COUNT"], "COUNT") if "COUNT" in fields else None,
        "until": _parse_until(fields["UNTIL"]) if "UNTIL" in fields else None,
    }
