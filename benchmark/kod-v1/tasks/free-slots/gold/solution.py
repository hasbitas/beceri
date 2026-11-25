def free_slots(busy, day_start, day_end, min_length):
    intervals = []
    for start, end in busy:
        if end <= start:
            continue
        start = max(start, day_start)
        end = min(end, day_end)
        if start < end:
            intervals.append((start, end))
    intervals.sort()

    result = []
    cursor = day_start
    for start, end in intervals:
        if start - cursor >= min_length:
            result.append((cursor, start))
        cursor = max(cursor, end)
    if day_end - cursor >= min_length:
        result.append((cursor, day_end))
    return result
