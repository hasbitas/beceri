def distance(a, b, limit=None):
    """Compute unit-cost Levenshtein distance, capped at limit + 1."""
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("a and b must be strings")
    if limit is not None:
        if isinstance(limit, bool) or not isinstance(limit, int):
            raise TypeError("limit must be an integer or None")
        if limit < 0:
            raise ValueError("limit must be nonnegative")
    if a == b:
        return 0
    if len(a) < len(b):
        a, b = b, a
    n, m = len(a), len(b)
    bound = n if limit is None else limit
    sentinel = bound + 1
    if n - m > bound:
        return sentinel
    if not b:
        return n

    previous = list(range(m + 1))
    for i, char_a in enumerate(a, 1):
        current = [sentinel] * (m + 1)
        current[0] = min(i, sentinel)
        for j in range(max(1, i - bound), min(m, i + bound) + 1):
            current[j] = min(
                previous[j] + 1,
                current[j - 1] + 1,
                previous[j - 1] + (char_a != b[j - 1]),
                sentinel,
            )
        if min(current) > bound:
            return sentinel
        previous = current
    return min(previous[m], sentinel)
