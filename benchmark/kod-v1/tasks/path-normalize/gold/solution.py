def normalize(path):
    """Normalize a POSIX path without consulting the filesystem."""
    if not isinstance(path, str):
        raise TypeError('path must be a str')
    absolute = path.startswith('/')
    parts = []
    for component in path.split('/'):
        if component in ('', '.'):
            continue
        if component == '..':
            if parts and parts[-1] != '..':
                parts.pop()
            elif not absolute:
                parts.append(component)
        else:
            parts.append(component)
    result = ('/' if absolute else '') + '/'.join(parts)
    if not result:
        result = '.'
    if path.endswith('/') and result != '/':
        result += '/'
    return result
