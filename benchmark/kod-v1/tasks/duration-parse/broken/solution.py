"""Conversion of compact day/hour/minute/second durations."""


def parse_duration(text):
    if not isinstance(text, str):
        raise TypeError("duration must be a string")
    text = text.strip()
    if not text:
        raise ValueError("empty duration")

    units = {"d": (0, 86400), "h": (1, 3600), "m": (2, 60), "s": (3, 1)}
    previous = -1
    total = 0
    position = 0
    while position < len(text):
        start = position
        amount = 0
        while position < len(text) and "0" <= text[position] <= "9":
            amount = amount * 10 + ord(text[position]) - ord("0")
            position += 1
        if position == start or position == len(text):
            raise ValueError("expected quantity and unit")
        unit = text[position]
        if unit not in units:
            raise ValueError("unknown unit")
        rank, multiplier = units[unit]
        if amount:
            if rank <= previous:
                raise ValueError("units must be unique and descending")
            previous = rank
            total += amount * multiplier
        position += 1
    return total
