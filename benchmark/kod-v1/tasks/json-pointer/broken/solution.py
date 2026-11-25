"""Plain JSON Pointer lookup."""


def _decode(token):
    i = 0
    while i < len(token):
        if token[i] == '~':
            if i + 1 >= len(token) or token[i + 1] not in '01':
                raise ValueError('Invalid pointer escape')
            i += 2
        else:
            i += 1
    return token.replace('~0', '~').replace('~1', '/')


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
            bound = str(len(current))
            if len(token) > len(bound) or (len(token) == len(bound) and token >= bound):
                raise KeyError(token)
            current = current[int(token)]
        else:
            raise KeyError(token)
    return current
