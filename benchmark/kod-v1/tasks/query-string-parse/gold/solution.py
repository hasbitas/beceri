"""Query-string parsing with per-component form decoding."""

from urllib.parse import unquote_plus


def parse_query(qs):
    if not isinstance(qs, str):
        raise TypeError("qs must be a str")
    if qs.startswith("?"):
        qs = qs[1:]
    result = {}
    for field in qs.split("&"):
        if not field:
            continue
        key, separator, value = field.partition("=")
        key = unquote_plus(key, encoding="utf-8", errors="replace")
        value = unquote_plus(value, encoding="utf-8", errors="replace")
        result.setdefault(key, []).append(value)
    return result
