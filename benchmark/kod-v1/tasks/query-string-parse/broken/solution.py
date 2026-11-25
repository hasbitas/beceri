"""Small form-style query-string parser."""

from urllib.parse import unquote_plus


def parse_query(qs):
    if not isinstance(qs, str):
        raise TypeError("qs must be a str")
    if qs.startswith("?"):
        qs = qs[1:]
    qs = unquote_plus(qs, encoding="utf-8", errors="replace")
    result = {}
    for field in qs.split("&"):
        if not field:
            continue
        key, separator, value = field.partition("=")
        result.setdefault(key, []).append(value)
    return result
