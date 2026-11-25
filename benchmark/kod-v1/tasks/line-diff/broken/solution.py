"""Deterministic line-level longest-common-subsequence diff."""


def diff(old_lines, new_lines):
    for lines in (old_lines, new_lines):
        if not isinstance(lines, (list, tuple)):
            raise TypeError('expected a list or tuple of strings')
        if any(not isinstance(line, str) for line in lines):
            raise TypeError('each line must be a string')

    m, n = len(old_lines), len(new_lines)
    lengths = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m - 1, -1, -1):
        for j in range(n - 1, -1, -1):
            if old_lines[i] == new_lines[j]:
                lengths[i][j] = 1 + lengths[i + 1][j + 1]
            else:
                lengths[i][j] = max(lengths[i + 1][j], lengths[i][j + 1])

    result = []
    i = j = 0
    while i < m and j < n:
        if old_lines[i] == new_lines[j]:
            result.append(('=', old_lines[i]))
            i += 1
            j += 1
        elif lengths[i + 1][j] > lengths[i][j + 1]:
            result.append(('-', old_lines[i]))
            i += 1
        else:
            result.append(('+', new_lines[j]))
            j += 1
    result.extend(('-', line) for line in old_lines[i:])
    result.extend(('+', line) for line in new_lines[j:])
    return result
