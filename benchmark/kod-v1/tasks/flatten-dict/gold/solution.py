"""Conversion between nested mappings and literal dotted paths."""


def flatten(data):
    if not isinstance(data, dict):
        raise TypeError('expected dict')
    result = {}

    def visit(mapping, prefix):
        for key, value in mapping.items():
            if not isinstance(key, str):
                raise TypeError('keys must be strings')
            if not key or '.' in key:
                raise ValueError('invalid segment')
            path = prefix + (key,)
            if isinstance(value, dict):
                if value:
                    visit(value, path)
                else:
                    result['.'.join(path)] = {}
            else:
                result['.'.join(path)] = value

    visit(data, ())
    return result


def unflatten(data):
    if not isinstance(data, dict):
        raise TypeError('expected dict')
    entries = []
    paths = set()
    for key, value in data.items():
        if not isinstance(key, str):
            raise TypeError('keys must be strings')
        path = tuple(key.split('.'))
        if any(not segment for segment in path):
            raise ValueError('empty segment')
        if isinstance(value, dict) and value:
            raise ValueError('nonempty dict leaf')
        entries.append((path, value))
        paths.add(path)
    for path in paths:
        for length in range(1, len(path)):
            if path[:length] in paths:
                raise ValueError('conflicting paths')
    result = {}
    for path, value in entries:
        node = result
        for segment in path[:-1]:
            node = node.setdefault(segment, {})
        node[path[-1]] = {} if isinstance(value, dict) else value
    return result
