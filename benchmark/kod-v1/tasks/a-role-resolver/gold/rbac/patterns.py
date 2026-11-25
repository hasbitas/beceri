"""Permission strings and wildcard patterns."""

import re

_SEGMENT = re.compile(r'[a-z0-9_-]+')


def _split(value, what):
    if type(value) is not str:
        raise TypeError(what + ' must be a str')
    if not value:
        raise ValueError(what + ' must not be empty')
    return value.split(':')


def validate_pattern(pattern):
    parts = _split(pattern, 'pattern')
    for index, part in enumerate(parts):
        if part == '*' or (part == '**' and index == len(parts) - 1):
            continue
        if not _SEGMENT.fullmatch(part):
            raise ValueError('bad pattern segment: %r' % part)


def validate_permission(permission):
    for part in _split(permission, 'permission'):
        if not _SEGMENT.fullmatch(part):
            raise ValueError('bad permission segment: %r' % part)


def matches(pattern, permission):
    validate_pattern(pattern)
    validate_permission(permission)
    pattern_parts = pattern.split(':')
    parts = permission.split(':')
    if pattern_parts[-1] == '**':
        pattern_parts = pattern_parts[:-1]
        if len(parts) <= len(pattern_parts):
            return False
        parts = parts[:len(pattern_parts)]
    elif len(pattern_parts) != len(parts):
        return False
    return all(p == '*' or p == q for p, q in zip(pattern_parts, parts))
