"""Plain JSON Pointer lookup."""


def _decode(token):
    result = []
    i = 0
    while i < len(token):
        ch = token[i]
        if ch == '~':
            if i + 1 >= len(token) or token[i + 1] not in '01':
                raise ValueError('Invalid pointer escape')
            result.append('~' if token[i + 1] == '0' else '/')
            i += 2
        else:
            result.append(ch)
            i += 1
    return ''.join(result)


def resolve(document, pointer):
    if not isinstance(pointer, str):
        raise TypeError('Pointer must be a string')
    if pointer == '':
        return document
    if not pointer.startswith('/'):
        raise ValueError('Pointer must start with slash')
    tokens = [_decode(token) for token in pointer[1:].split('/')]
    current = document
    for token in tokens:
        if isinstance(current, dict):
            current = current[token]
        elif isinstance(current, list):
            if not token or any(c < '0' or c > '9' for c in token):
                raise KeyError(token)
            if len(token) > 1 and token[0] == '0':
                raise KeyError(token)
            # Compare decimal strings before conversion, including huge indexes.
            bound = str(len(current))
            if len(token) > len(bound) or (len(token) == len(bound) and token >= bound):
                raise KeyError(token)
            current = current[int(token)]
        else:
            raise KeyError(token)
    return current
