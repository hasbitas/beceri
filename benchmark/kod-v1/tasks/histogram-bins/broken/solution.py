"""Equal-width histogram with exact boundary comparisons."""

import math
from fractions import Fraction


def _number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("expected an int or float, excluding bool")
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("expected a finite number")
    return Fraction(value)


def histogram(values, bins, low, high):
    if isinstance(bins, bool) or not isinstance(bins, int):
        raise TypeError("bins must be an integer")
    if bins <= 0:
        raise ValueError("bins must be positive")
    lower = _number(low)
    upper = _number(high)
    if lower >= upper:
        raise ValueError("low must be less than high")
    counts = [0] * bins
    span = upper - lower
    for raw in values:
        value = _number(raw)
        if value < lower or value >= upper:
            continue
        index = (value - lower) * bins // span
        counts[index] += 1
    return counts
