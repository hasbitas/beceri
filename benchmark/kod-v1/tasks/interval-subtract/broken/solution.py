def subtract(base, holes):
    """Clip the holes, sort them, and collect gaps between them."""
    left, right = base
    clipped = []
    for start, end in holes:
        start = max(left, start)
        end = min(right, end)
        if start < end:
            clipped.append((start, end))
    clipped.sort()

    pieces = []
    cursor = left
    for start, end in clipped:
        if cursor < start:
            pieces.append((cursor, start))
        cursor = end
    if cursor < right:
        pieces.append((cursor, right))
    return pieces
