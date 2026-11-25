"""Semantic version comparison with validation."""

import re

_VERSION = re.compile(
    r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)"
    r"(?:-([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?"
)


def _parse(text):
    match = _VERSION.fullmatch(text)
    if match is None:
        raise ValueError("Invalid semantic version")
    major, minor, patch, pre, _build = match.groups()
    identifiers = None if pre is None else pre.split(".")
    if identifiers is not None:
        for item in identifiers:
            if item.isdigit() and len(item) > 1 and item[0] == "0":
                raise ValueError("Leading zero in numeric pre-release identifier")
    return (major, minor, patch), identifiers


def _cmp(a, b):
    return (a > b) - (a < b)


def _numeric(a, b):
    return _cmp(len(a), len(b)) or _cmp(a, b)


def compare(a, b):
    if not isinstance(a, str) or not isinstance(b, str):
        raise TypeError("Versions must be strings")
    core_a, pre_a = _parse(a)
    core_b, pre_b = _parse(b)
    for left, right in zip(core_a, core_b):
        result = _numeric(left, right)
        if result:
            return result
    if pre_a is None or pre_b is None:
        return _cmp(pre_a is None, pre_b is None)
    for left, right in zip(pre_a, pre_b):
        left_numeric, right_numeric = left.isdigit(), right.isdigit()
        if left_numeric != right_numeric:
            result = -1 if left_numeric else 1
        else:
            result = _cmp(left, right)
        if result:
            return result
    return _cmp(len(pre_a), len(pre_b))
