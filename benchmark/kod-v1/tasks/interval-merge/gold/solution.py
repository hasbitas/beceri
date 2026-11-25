def merge(intervals):
    if not isinstance(intervals, (list, tuple)):
        raise TypeError('intervals must be a list or tuple')
    checked = []
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
        checked.append((start, end))

    result = []
    for start, end in sorted(checked):
        if result and start <= result[-1][1]:
            result[-1][1] = max(result[-1][1], end)
        else:
            result.append([start, end])
    return result
