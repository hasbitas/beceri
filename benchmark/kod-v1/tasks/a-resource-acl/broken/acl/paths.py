"""Resource paths as tuples of segments."""


def split_path(path):
    if type(path) is not str:
        raise TypeError('path must be a str')
    if not path.startswith('/'):
        raise ValueError('path must be absolute')
    if path == '/':
        return ()
    body = path[1:].strip('/')
    segments = tuple(body.split('/'))
    for segment in segments:
        if segment in ('', '.', '..'):
            raise ValueError('bad path segment: %r' % segment)
    return segments


def lineage(segments):
    return [tuple(segments[:count]) for count in range(len(segments) + 1)]


def join(segments):
    return '/' + '/'.join(segments)
