"""Sliding-window maximum with strict integer validation."""

from collections import deque


def window_max(values, k):
    if not isinstance(values, (list, tuple)):
        raise TypeError("values must be a list or tuple")
    if isinstance(k, bool) or not isinstance(k, int):
        raise TypeError("k must be an integer")
    if k <= 0:
        raise ValueError("k must be positive")
    for value in values:
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError("values must contain integers")
    if k > len(values):
        return []

    candidates = deque()
    result = []
    for i, value in enumerate(values):
        while candidates and candidates[0] < i - k:
            candidates.popleft()
        while candidates and values[candidates[-1]] <= value:
            candidates.pop()
        candidates.append(i)
        if i >= k - 1:
            result.append(values[candidates[0]])
    return result
