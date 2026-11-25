"""Canonical run-length codec for ASCII letters."""


def _letter(ch):
    return 'a' <= ch <= 'z' or 'A' <= ch <= 'Z'


def encode(text):
    if not isinstance(text, str):
        raise TypeError('expected str')
    if any(not _letter(ch) for ch in text):
        raise ValueError('expected ASCII letters')
    parts = []
    i = 0
    while i < len(text):
        j = i + 1
        while j < len(text) and text[j] == text[i]:
            j += 1
        parts.append(str(j - i) + text[i])
        i = j
    return ''.join(parts)


def decode(encoded):
    if not isinstance(encoded, str):
        raise TypeError('expected str')
    parts = []
    previous = None
    i = 0
    while i < len(encoded):
        start = i
        while i < len(encoded) and '0' <= encoded[i] <= '9':
            i += 1
        digits = encoded[start:i]
        if not digits or digits[0] == '0':
            raise ValueError('invalid count')
        if i == len(encoded) or not _letter(encoded[i]):
            raise ValueError('missing ASCII letter')
        letter = encoded[i]
        if letter == previous:
            raise ValueError('adjacent equal runs')
        parts.append(letter * int(digits))
        previous = letter
        i += 1
    return ''.join(parts)
