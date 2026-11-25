"""Unicode case conversion with Turkish dotted and dotless I support."""


def tr_upper(text):
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    special = {"i": "İ", "ı": "I"}
    return "".join(special[ch] if ch in special else ch.upper() for ch in text)


def tr_lower(text):
    if not isinstance(text, str):
        raise TypeError("text must be a str")
    special = {"I": "ı", "İ": "i"}
    return "".join(special[ch] if ch in special else ch.lower() for ch in text)
