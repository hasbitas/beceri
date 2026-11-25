def justify(words, width):
    lines = []
    start = 0
    while start < len(words):
        end = start + 1
        letters = len(words[start])
        while end < len(words) and letters + len(words[end]) + end - start <= width:
            letters += len(words[end])
            end += 1
        count = end - start
        if end == len(words) or count == 1:
            line = ' '.join(words[start:end]).ljust(width)
        else:
            base, extra = divmod(width - letters, count - 1)
            parts = []
            for offset in range(count - 1):
                parts.append(words[start + offset])
                parts.append(' ' * (base + (offset < extra)))
            parts.append(words[end - 1])
            line = ''.join(parts)
        lines.append(line)
        start = end
    return lines
