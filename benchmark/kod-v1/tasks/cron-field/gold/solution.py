"""Numeric cron field expansion."""
import re

_ITEM = re.compile(r'(\*|[0-9]+(?:-[0-9]+)?)(?:/([0-9]+))?', re.ASCII)


def _number(text):
    value = 0
    for char in text:
        value = value * 10 + ord(char) - ord('0')
    return value


def expand(field, low, high):
    if not isinstance(field, str):
        raise TypeError('field must be a string')
    if (not isinstance(low, int) or isinstance(low, bool)
            or not isinstance(high, int) or isinstance(high, bool)):
        raise TypeError('bounds must be integers')
    if low < 0 or high < low:
        raise ValueError('invalid bounds')
    result = set()
    for item in field.split(','):
        match = _ITEM.fullmatch(item)
        if match is None:
            raise ValueError('invalid item')
        base, step_text = match.groups()
        if step_text is not None and base != '*' and '-' not in base:
            raise ValueError('single numbers cannot have steps')
        step = 1 if step_text is None else _number(step_text)
        if step == 0:
            raise ValueError('step must be positive')
        if base == '*':
            start, end = low, high
        elif '-' in base:
            left, right = base.split('-')
            start, end = _number(left), _number(right)
        else:
            start = end = _number(base)
        if not low <= start <= end <= high:
            raise ValueError('invalid interval')
        result.update(range(start, end + 1, step))
    return sorted(result)
