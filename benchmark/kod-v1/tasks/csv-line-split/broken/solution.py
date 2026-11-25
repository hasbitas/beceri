def split_csv_line(line):
    """Decode a single strict CSV record without a line terminator."""
    if not isinstance(line, str):
        raise TypeError("line must be a string")
    if '\r' in line or '\n' in line:
        raise ValueError("record terminators are not allowed")

    fields = []
    i = 0
    n = len(line)
    while True:
        field = []
        if i < n and line[i] == '"':
            i += 1
            while True:
                if i == n:
                    raise ValueError("unterminated quoted field")
                if line[i] != '"':
                    field.append(line[i])
                    i += 1
                elif i + 1 < n and line[i + 1] == '"':
                    field.append('"')
                    i += 2
                else:
                    i += 1
                    break
            if i < n and line[i] != ',':
                raise ValueError("unexpected character after closing quote")
        else:
            while i < n and line[i] != ',':
                if line[i] == '"':
                    raise ValueError("quote in unquoted field")
                field.append(line[i])
                i += 1
        fields.append(''.join(field))
        if i == n:
            return fields
        i += 1
        if i == n:
            return fields

