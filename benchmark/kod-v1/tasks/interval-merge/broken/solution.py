def merge(intervals):
    if not isinstance(intervals, (list, tuple)):
        raise TypeError('intervals must be a list or tuple')
    ordered = []
    for interval in intervals:
        if not isinstance(interval, (list, tuple)):
            raise TypeError('each interval must be a list or tuple')
        if len(interval) != 2:
            raise ValueError('each interval must have two endpoints')
        start, end = interval
        if (not isinstance(start, int) or isinstance(start, bool)
                or not isinstance(end, int) or isinstance(end, bool)):
            raise TypeError('endpoints must be non-boolean integers')
        if start > end:
            raise ValueError('start must not exceed end')
        ordered.append((start, end))
    ordered.sort()

    merged = []
    for start, end in ordered:
        if not merged or start > merged[-1][1] + 1:
            merged.append([start, end])
        else:
            merged[-1][1] = max(merged[-1][1], end)
    return merged
