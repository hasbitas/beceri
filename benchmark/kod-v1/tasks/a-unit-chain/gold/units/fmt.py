"""Exact number parsing, rounding and formatting."""

import re
from fractions import Fraction

_DECIMAL = re.compile(r'[+-]?[0-9]+(\.[0-9]+)?')


def to_fraction(value):
    if type(value) is int or isinstance(value, Fraction):
        return Fraction(value)
    if type(value) is str:
        if not _DECIMAL.fullmatch(value):
            raise ValueError('not a decimal number: %r' % value)
        return Fraction(value)
    raise TypeError('value must be an int, Fraction or decimal str')


def _check_places(places):
    if type(places) is not int:
        raise TypeError('places must be an int')
    if places < 0:
        raise ValueError('places must not be negative')


def _check_amount(x):
    if type(x) is not int and not isinstance(x, Fraction):
        raise TypeError('x must be an int or Fraction')


def quantize(x, places):
    _check_amount(x)
    _check_places(places)
    scaled = Fraction(x) * 10 ** places
    quotient, remainder = divmod(abs(scaled.numerator), scaled.denominator)
    if 2 * remainder >= scaled.denominator:
        quotient += 1
    if scaled < 0:
        quotient = -quotient
    return Fraction(quotient, 10 ** places)


def format_decimal(x, places):
    _check_amount(x)
    _check_places(places)
    units = int(quantize(x, places) * 10 ** places)
    digits = str(abs(units)).rjust(places + 1, '0')
    if places:
        digits = digits[:-places] + '.' + digits[-places:]
    return ('-' if units < 0 else '') + digits
