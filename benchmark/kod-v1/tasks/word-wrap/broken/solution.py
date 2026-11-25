def wrap(text, width):
    if width <= 0:
        raise ValueError("width must be positive")

    lines = []
    current = ""
    for word in text.split():
        if len(word) > width:
            if current:
                lines.append(current)
                current = ""
            while len(word) >= width:
                lines.append(word[:width])
                word = word[width:]
            current = word
        elif not current:
            current = word
        elif len(current) + 1 + len(word) < width:
            current += " " + word
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)
