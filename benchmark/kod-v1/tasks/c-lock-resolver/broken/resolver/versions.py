"""Version strings of the form MAJOR.MINOR.PATCH."""

import re

_VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")


def parse_version(text):
    if not isinstance(text, str):
        raise TypeError("version must be a str")
    match = _VERSION.fullmatch(text)
    if match is None:
        raise ValueError("malformed version: %r" % (text,))
    return tuple(int(part) for part in match.groups())


def format_version(parts):
    if len(parts) != 3:
        raise ValueError("a version has exactly three parts")
    return ".".join(str(part) for part in parts)


def newest(versions, major):
    texts = list(versions)
    for text in texts:
        parse_version(text)
    matching = [text for text in texts if parse_version(text)[0] == major]
    if not matching:
        return None
    return max(matching)
