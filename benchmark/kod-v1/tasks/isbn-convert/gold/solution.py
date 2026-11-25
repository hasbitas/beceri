"""Validated ISBN-10 and ISBN-13 conversion."""


def _normalize(value):
    if not isinstance(value, str):
        raise TypeError("ISBN must be a string")
    return value.replace(" ", "").replace("-", "")


def _digits(text):
    return all("0" <= ch <= "9" for ch in text)


def _check13(body):
    return str(-sum(int(ch) * (1 if i % 2 == 0 else 3)
                    for i, ch in enumerate(body)) % 10)


def _check10(body):
    digit = -sum(int(ch) * (10 - i) for i, ch in enumerate(body)) % 11
    return "X" if digit == 10 else str(digit)


def isbn10_to_13(value):
    text = _normalize(value)
    if (len(text) != 10 or not _digits(text[:9])
            or text[-1] not in "0123456789Xx"):
        raise ValueError("Invalid ISBN-10 format")
    if text[-1].upper() != _check10(text[:9]):
        raise ValueError("Invalid ISBN-10 checksum")
    body = "978" + text[:9]
    return body + _check13(body)


def isbn13_to_10(value):
    text = _normalize(value)
    if len(text) != 13 or not _digits(text) or text[:3] not in ("978", "979"):
        raise ValueError("Invalid ISBN-13 format")
    if text[-1] != _check13(text[:12]):
        raise ValueError("Invalid ISBN-13 checksum")
    if text.startswith("979"):
        raise ValueError("ISBN-13 has no ISBN-10 equivalent")
    body = text[3:12]
    return body + _check10(body)
