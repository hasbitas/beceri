"""Validation of JSON-like values against a small schema dialect."""

from collections import namedtuple

Issue = namedtuple("Issue", "path code")

_TYPES = ("object", "array", "string", "integer", "number", "boolean", "null")


def _is_type(value, name):
    if name == "object":
        return isinstance(value, dict)
    if name == "array":
        return isinstance(value, list)
    if name == "string":
        return isinstance(value, str)
    if name == "integer":
        return isinstance(value, int)
    if name == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    if name == "boolean":
        return isinstance(value, bool)
    return value is None


def _in_enum(value, options):
    return any(type(value) is type(option) and value == option for option in options)


def _check(schema, value, path, issues):
    if not isinstance(schema, dict):
        raise TypeError("a schema must be a dict")
    if "type" in schema:
        if schema["type"] not in _TYPES:
            raise ValueError("unknown type: %r" % (schema["type"],))
        if not _is_type(value, schema["type"]):
            issues.append(Issue(path, "type"))
            return
    if "enum" in schema and not _in_enum(value, schema["enum"]):
        issues.append(Issue(path, "enum"))
    if isinstance(value, str):
        if "min_length" in schema and len(value) < schema["min_length"]:
            issues.append(Issue(path, "min_length"))
        if "max_length" in schema and len(value) > schema["max_length"]:
            issues.append(Issue(path, "max_length"))
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        if "minimum" in schema and value < schema["minimum"]:
            issues.append(Issue(path, "minimum"))
        if "maximum" in schema and value > schema["maximum"]:
            issues.append(Issue(path, "maximum"))
    if isinstance(value, dict):
        for key in schema.get("required", ()):
            if key not in value:
                issues.append(Issue(path, "required"))
        properties = schema.get("properties", {})
        for key, sub_schema in properties.items():
            if key in value:
                _check(sub_schema, value[key], path + (key,), issues)
        if not schema.get("additional", True):
            for key in sorted(value):
                if key not in properties:
                    issues.append(Issue(path + (key,), "unexpected"))
    if isinstance(value, list):
        if "min_items" in schema and len(value) < schema["min_items"]:
            issues.append(Issue(path, "min_items"))
        if "max_items" in schema and len(value) > schema["max_items"]:
            issues.append(Issue(path, "max_items"))
        if "items" in schema:
            for index, element in enumerate(value):
                _check(schema["items"], element, path + (index,), issues)


def validate(schema, value):
    issues = []
    _check(schema, value, (), issues)
    return issues
