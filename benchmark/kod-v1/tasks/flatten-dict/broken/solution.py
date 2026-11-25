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
    result = {}
    for key, value in data.items():
        if not isinstance(key, str):
            raise TypeError('keys must be strings')
        segments = key.split('.')
        if any(not segment for segment in segments):
            raise ValueError('empty segment')
        if isinstance(value, dict) and value:
            raise ValueError('nonempty dict leaf')
        node = result
        for segment in segments[:-1]:
            if segment not in node:
                node[segment] = {}
            elif not isinstance(node[segment], dict):
                raise ValueError('conflicting paths')
            node = node[segment]
        if segments[-1] in node:
            raise ValueError('conflicting paths')
        node[segments[-1]] = {} if isinstance(value, dict) else value
    return result
