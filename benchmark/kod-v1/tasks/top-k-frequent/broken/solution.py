"""Frequency ranking of exact string values."""


def top_k(items, k):
    if isinstance(k, bool) or not isinstance(k, int):
        raise TypeError("k must be an integer other than bool")
    if k < 0:
        raise ValueError("k must be nonnegative")

    counts = {}
    for item in items:
        if not isinstance(item, str):
            raise TypeError("items must contain strings")
        counts[item] = counts.get(item, 0) + 1

    ranked = sorted(counts, key=lambda item: (-counts[item], item.lower(), item))
    return ranked[:k]
