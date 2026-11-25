"""Convert integer text between bases."""

_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def convert(number_text, from_base, to_base):
    for base in (from_base, to_base):
        if not isinstance(base, int) or isinstance(base, bool):
            raise TypeError("bases must be integers")
        if not 2 <= base <= 36:
            raise ValueError("base out of range")
    if not isinstance(number_text, str):
        raise TypeError("number_text must be a string")
    value = int(number_text, from_base)
    if value == 0:
        return "0"
    negative = value < 0
    value = abs(value)
    result = []
    while value:
        value, digit = divmod(value, to_base)
        result.append(_DIGITS[digit])
    return ("-" if negative else "") + "".join(reversed(result))
