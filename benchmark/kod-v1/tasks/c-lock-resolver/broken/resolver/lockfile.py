"""Text format for resolved dependency sets."""

import re

from .solver import resolve
from .versions import parse_version

HEADER = "# lock v1"
_LINE = re.compile(r"([a-z][a-z0-9-]*)==([0-9.]+)(?: requires (.+))?")
_DEPENDENCY = re.compile(r"([a-z][a-z0-9-]*)@(0|[1-9][0-9]*)")


def render_lock(registry, resolution):
    lines = [HEADER]
    for name in resolution:
        version = resolution[name]
        dependencies = registry[name][version]
        line = "%s==%s" % (name, version)
        if dependencies:
            line += " requires " + ",".join("%s@%d" % (dep, dependencies[dep]) for dep in sorted(dependencies))
        lines.append(line)
    return "\n".join(lines) + "\n"


def parse_lock(text):
    if not isinstance(text, str):
        raise TypeError("lock text must be a str")
    if "\r" in text:
        raise ValueError("carriage returns are not allowed")
    lines = text.split("\n")
    if lines[0] != HEADER:
        raise ValueError("missing lock header")
    entries = {}
    for line in lines[1:]:
        if line == "" or line.startswith("#"):
            continue
        match = _LINE.fullmatch(line)
        if match is None:
            raise ValueError("malformed lock line: %r" % (line,))
        name, version, requires = match.groups()
        parse_version(version)
        dependencies = {}
        if requires is not None:
            for item in requires.split(","):
                piece = _DEPENDENCY.fullmatch(item)
                if piece is None:
                    raise ValueError("malformed dependency: %r" % (item,))
                if piece.group(1) in dependencies:
                    raise ValueError("duplicate dependency: %s" % (piece.group(1),))
                dependencies[piece.group(1)] = int(piece.group(2))
        entries[name] = (version, dependencies)
    return entries


def generate_lock(registry, requirements):
    return render_lock(registry, resolve(registry, requirements))
