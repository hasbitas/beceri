"""Conversion between flag expressions and masks."""

_FLAGS = (("READ", 1), ("WRITE", 2), ("EXECUTE", 4), ("HIDDEN", 8), ("ARCHIVE", 16))
_VALUES = dict(_FLAGS)
_ALL = 31


def parse_flags(text):
    if not isinstance(text, str):
        raise TypeError("text must be a string")
    text = text.strip()
    if not text:
        return 0
    tokens = [part.strip() for part in text.split(",")]
    if tokens == ["NONE"]:
        return 0
    additions = 0
    removals = 0
    for token in tokens:
        remove = token.startswith("!")
        name = token[1:] if remove else token
        if name == "ALL":
            bits = _ALL
        elif name in _VALUES:
            bits = _VALUES[name]
        else:
            raise ValueError("invalid flag token")
        if remove:
            removals |= bits
        else:
            additions |= bits
    return additions & ~removals


def format_flags(mask):
    if isinstance(mask, bool) or not isinstance(mask, int):
        raise TypeError("mask must be an integer, not bool")
    if mask < 0 or mask & ~_ALL:
        raise ValueError("mask contains unsupported bits")
    return ",".join(name for name, bits in _FLAGS if mask & bits) or "NONE"
