def justify(words, width):
    result = []
    i = 0
    while i < len(words):
        j = i + 1
        letters = len(words[i])
        while j < len(words) and letters + len(words[j]) + j - i <= width:
            letters += len(words[j])
            j += 1
        row = words[i:j]
        if j == len(words) or len(row) == 1:
            result.append(' '.join(row).ljust(width))
        else:
            gaps = len(row) - 1
            spaces, remainder = divmod(width - letters, gaps)
            line = row[0]
            for gap in range(gaps):
                padding = spaces + (gap >= gaps - remainder)
                line += ' ' * padding + row[gap + 1]
            result.append(line)
        i = j
    return result
