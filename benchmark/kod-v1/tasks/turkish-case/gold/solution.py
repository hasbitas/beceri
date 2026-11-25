"""Turkish I substitutions followed by standard Unicode case conversion."""

_UPPER = str.maketrans({"i": "İ", "ı": "I"})
_LOWER = str.maketrans({"I": "ı", "İ": "i"})


def tr_upper(text):
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    return str.upper(str.translate(text, _UPPER))


def tr_lower(text):
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    return str.lower(str.translate(text, _LOWER))
