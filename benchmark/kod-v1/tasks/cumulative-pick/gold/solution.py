"""Deterministic cumulative weighted selection."""
import math
from fractions import Fraction


def pick(weights, r):
    if not isinstance(weights, (list, tuple)):
        raise TypeError('weights must be a list or tuple')
    if type(r) not in (int, float):
        raise TypeError('r must be an int or float')
    if (type(r) is float and not math.isfinite(r)) or not 0 <= r < 1:
        raise ValueError('r must be finite and in [0, 1)')
    if not weights:
        raise ValueError('weights must not be empty')
    values = []
    for weight in weights:
        if type(weight) not in (int, float):
            raise TypeError('weights must contain ints or floats')
        if (type(weight) is float and not math.isfinite(weight)) or weight < 0:
            raise ValueError('weights must be finite and nonnegative')
        values.append(Fraction(weight))
    total = sum(values, Fraction(0))
    if total == 0:
        raise ValueError('at least one weight must be positive')
    target = Fraction(r) * total
    cumulative = Fraction(0)
    for index, weight in enumerate(values):
        cumulative += weight
        if weight > 0 and target < cumulative:
            return index
    raise AssertionError('valid target must be covered')
