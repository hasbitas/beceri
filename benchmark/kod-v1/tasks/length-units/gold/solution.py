"""Parse compound lengths with a single sign for the whole quantity."""
import math
import re
from decimal import Decimal

_WHITESPACE = " \t\r\n\f\v"
_COMPONENT = re.compile(
    r"([0-9]+(?:\.[0-9]*)?|\.[0-9]+)[ \t\r\n\f\v]*(mm|cm|in|ft|yd|m)",
    re.IGNORECASE | re.ASCII,
)
_FACTORS = {"m": "1", "cm": "0.01", "mm": "0.001",
            "in": "0.0254", "ft": "0.3048", "yd": "0.9144"}


def to_meters(text):
    if not isinstance(text, str):
        raise TypeError("length must be a string")
    text = text.strip(_WHITESPACE)
    sign = 1.0
    if text.startswith(("+", "-")):
        sign = -1.0 if text[0] == "-" else 1.0
        text = text[1:]
    if not text:
        raise ValueError("missing length")
    pos = 0
    seen = set()
    total = 0.0
    while pos < len(text):
        match = _COMPONENT.match(text, pos)
        if match is None:
            raise ValueError("invalid length component")
        number, unit = match.groups()
        unit = unit.lower()
        if unit in seen:
            raise ValueError("repeated unit")
        seen.add(unit)
        magnitude = float(Decimal(number) * Decimal(_FACTORS[unit]))
        if not math.isfinite(magnitude):
            raise ValueError("component exceeds float range")
        total += magnitude
        if not math.isfinite(total):
            raise ValueError("total exceeds float range")
        pos = match.end()
        while pos < len(text) and text[pos] in _WHITESPACE:
            pos += 1
    return sign * total
