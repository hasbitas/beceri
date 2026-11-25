"""Validated linearly interpolated percentiles."""
import math


def _number(value):
    if type(value) not in (int, float):
        raise TypeError('expected a built-in int or float')
    try:
        converted = float(value)
    except OverflowError:
        raise ValueError('number is not a finite float') from None
    if not math.isfinite(converted):
        raise ValueError('number is not finite')
    return converted


def percentile(values, p):
    if not isinstance(values, (list, tuple)):
        raise TypeError('values must be a list or tuple')
    percent = _number(p)
    if not 0.0 <= percent <= 100.0:
        raise ValueError('percentile out of range')
    if not values:
        raise ValueError('empty observations')
    ordered = sorted(_number(value) for value in values)
    rank = (len(ordered) - 1) * (percent / 100.0)
    lower = math.floor(rank)
    fraction = rank - lower
    if fraction == 0.0:
        return ordered[lower]
    return (1.0 - fraction) * ordered[lower] + fraction * ordered[lower + 1]
