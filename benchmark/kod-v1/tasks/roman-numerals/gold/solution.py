"""Strict conversion between integers and canonical Roman numerals."""

_PAIRS = (
    (1000, 'M'), (900, 'CM'), (500, 'D'), (400, 'CD'),
    (100, 'C'), (90, 'XC'), (50, 'L'), (40, 'XL'),
    (10, 'X'), (9, 'IX'), (5, 'V'), (4, 'IV'), (1, 'I'),
)
_VALUES = dict(I=1, V=5, X=10, L=50, C=100, D=500, M=1000)


def to_roman(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError('value must be an integer, not bool')
    if not 1 <= value <= 3999:
        raise ValueError('value must be between 1 and 3999')
    parts = []
    for amount, symbol in _PAIRS:
        count, value = divmod(value, amount)
        parts.append(symbol * count)
    return ''.join(parts)


def from_roman(text):
    if not isinstance(text, str):
        raise TypeError('text must be a string')
    if not text or any(char not in _VALUES for char in text):
        raise ValueError('invalid Roman numeral')
    total = 0
    for index, char in enumerate(text):
        value = _VALUES[char]
        if index + 1 < len(text) and value < _VALUES[text[index + 1]]:
            total -= value
        else:
            total += value
    if not 1 <= total <= 3999 or to_roman(total) != text:
        raise ValueError('non-canonical Roman numeral')
    return total
