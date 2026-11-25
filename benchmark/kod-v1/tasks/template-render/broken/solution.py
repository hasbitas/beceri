"""Small, single-pass template renderer."""


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
            if not name.isidentifier():
                raise ValueError("Invalid placeholder name")
            result.append(str(values.get(name, "")))
            i = end + 2
        elif char == "}":
            raise ValueError("Unexpected closing brace")
        else:
            result.append(char)
            i += 1
    return "".join(result)
