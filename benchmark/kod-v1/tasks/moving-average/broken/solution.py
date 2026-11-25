import math
from collections import deque


def moving_average(values, window, partial=False):
    if type(window) is not int:
        raise TypeError('window must be an int')
    if window <= 0:
        raise ValueError('window must be positive')
    if type(partial) is not bool:
        raise TypeError('partial must be a bool')

    result = []
    recent = deque()
    for value in values:
        if type(value) not in (int, float):
            raise TypeError('values must contain ints or floats')
        number = float(value)
        if not math.isfinite(number):
            raise ValueError('values must be finite')
        recent.append(number)
        if len(recent) > window:
            recent.popleft()
        if partial or len(recent) == window:
            result.append(math.fsum(recent) / window)
    return result
