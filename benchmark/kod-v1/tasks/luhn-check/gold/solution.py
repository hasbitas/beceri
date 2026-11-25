"""Luhn validation and check-digit generation for formatted digit strings."""


def _digits(text):
    if not isinstance(text, str):
        raise TypeError("expected a string")
    digits = []
    for char in text:
        if '0' <= char <= '9':
            digits.append(ord(char) - ord('0'))
        elif char not in ' -':
            raise ValueError("invalid character")
    return digits


def _checksum(digits):
    total = 0
    for position, digit in enumerate(reversed(digits)):
        if position % 2:
            digit *= 2
            if digit > 9:
                digit -= 9
        total += digit
    return total % 10


def luhn_valid(text):
    digits = _digits(text)
    return bool(digits) and _checksum(digits) == 0


def luhn_check_digit(text):
    digits = _digits(text)
    if not digits:
        raise ValueError("payload must contain a digit")
    return str((-_checksum(digits + [0])) % 10)
