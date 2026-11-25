"""Small, single-pass template renderer."""

import re

_NAME = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\Z")


def render(template, values):
    result = []
    i = 0
    while i < len(template):
        char = template[i]
        if char == "\\":
            if i + 1 == len(template) or template[i + 1] not in "\\{}":
                raise ValueError("Invalid escape")
            result.append(template[i + 1])
            i += 2
        elif char == "{":
            if not template.startswith("{{", i):
                raise ValueError("Isolated opening brace")
            end = template.find("}}", i + 2)
            if end == -1:
                raise ValueError("Unclosed placeholder")
            name = template[i + 2:end]
            if _NAME.fullmatch(name) is None:
                raise ValueError("Invalid placeholder name")
            try:
                value = values[name]
            except KeyError:
                raise KeyError(name) from None
            result.append(str(value))
            i = end + 2
        elif char == "}":
            raise ValueError("Unexpected closing brace")
        else:
            result.append(char)
            i += 1
    return "".join(result)
