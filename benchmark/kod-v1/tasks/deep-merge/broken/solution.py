"""Recursive dictionary merging."""

from copy import deepcopy


def deep_merge(base, override):
    result = deepcopy(base)
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        elif isinstance(value, dict):
            result[key] = value.copy()
        elif isinstance(value, list):
            result[key] = value[:]
        else:
            result[key] = value
    return result
