"""Numeric dotted-version constraint evaluation."""

import re

_WS = " \t\r\n\v\f"
_VERSION = re.compile(r"[0-9]+(?:\.[0-9]+)*", re.ASCII)
_OPERATORS = ("==", "!=", "<=", ">=", "<", ">")


def _parse_version(text):
    text = text.strip(_WS)
    if _VERSION.fullmatch(text) is None:
        raise ValueError("invalid version")
    result = []
    for component in text.split("."):
        value = 0
        for digit in component:
            value = value * 10 + ord(digit) - ord("0")
        result.append(value)
    return tuple(result)


def _compare(left, right):
    return (left > right) - (left < right)


def satisfies(version, spec):
    if not isinstance(version, str) or not isinstance(spec, str):
        raise TypeError("version and spec must be strings")
    current = _parse_version(version)
    spec = spec.strip(_WS)
    constraints = []
    if spec:
        for field in spec.split(","):
            field = field.strip(_WS)
            operator = "=="
            for candidate in _OPERATORS:
                if field.startswith(candidate):
                    operator = candidate
                    field = field[len(candidate):]
                    break
            constraints.append((operator, _parse_version(field)))
    for operator, target in constraints:
        comparison = _compare(current, target)
        accepted = {
            "==": comparison == 0,
            "!=": comparison != 0,
            "<": comparison < 0,
            "<=": comparison <= 0,
            ">": comparison > 0,
            ">=": comparison >= 0,
        }[operator]
        if not accepted:
            return False
    return True
