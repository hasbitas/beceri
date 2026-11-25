"""Integer numeral conversion with an ASCII-only grammar."""

_DIGITS = "0123456789abcdefghijklmnopqrstuvwxyz"


def convert(number_text, from_base, to_base):
    for base in (from_base, to_base):
        if not isinstance(base, int) or isinstance(base, bool):
            raise TypeError("bases must be integers")
        if not 2 <= base <= 36:
            raise ValueError("base out of range")
    if not isinstance(number_text, str):
        raise TypeError("number_text must be a string")
    negative = number_text.startswith("-")
    digits = number_text[1:] if number_text.startswith(("+", "-")) else number_text
    if not digits:
        raise ValueError("missing digits")
    value = 0
    for char in digits:
        if "0" <= char <= "9":
            digit = ord(char) - ord("0")
        elif "a" <= char <= "z":
            digit = ord(char) - ord("a") + 10
        elif "A" <= char <= "Z":
            digit = ord(char) - ord("A") + 10
        else:
            raise ValueError("invalid character")
        if digit >= from_base:
            raise ValueError("digit out of range")
        value = value * from_base + digit
    if value == 0:
        return "0"
    result = []
    while value:
        value, digit = divmod(value, to_base)
        result.append(_DIGITS[digit])
    return ("-" if negative else "") + "".join(reversed(result))
