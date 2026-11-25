from collections import deque


def allowed(timestamps, limit, window):
    if (not isinstance(limit, int) or isinstance(limit, bool)
            or limit < 0):
        raise ValueError('limit must be a nonnegative integer')
    if (not isinstance(window, int) or isinstance(window, bool)
            or window <= 0):
        raise ValueError('window must be a positive integer')
    if not isinstance(timestamps, list):
        raise ValueError('timestamps must be a list')
    previous = -1
    for t in timestamps:
        if (not isinstance(t, int) or isinstance(t, bool)
                or t < 0 or t < previous):
            raise ValueError('invalid timestamp sequence')
        previous = t

    active = deque()
    result = []
    for t in timestamps:
        cutoff = t - window
        while active and active[0] < cutoff:
            active.popleft()
        admit = len(active) < limit
        result.append(admit)
        if admit:
            active.append(t)
    return result
