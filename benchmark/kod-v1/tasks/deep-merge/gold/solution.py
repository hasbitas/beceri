"""Recursive dictionary merging with independently owned output containers."""

from copy import deepcopy


def deep_merge(base, override):
    result = {}
    for key, value in base.items():
        if key not in override:
            result[key] = deepcopy(value)
        elif isinstance(value, dict) and isinstance(override[key], dict):
            result[key] = deep_merge(value, override[key])
        else:
            result[key] = deepcopy(override[key])
    for key, value in override.items():
        if key not in base:
            result[key] = deepcopy(value)
    return result
