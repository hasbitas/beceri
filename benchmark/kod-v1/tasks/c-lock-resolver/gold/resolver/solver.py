"""Resolution of a registry of packages against major-version requirements."""

from collections import deque

from .versions import newest


class ResolutionError(Exception):
    pass


class ConflictError(ResolutionError):
    pass


def _check_major(major):
    if isinstance(major, bool) or not isinstance(major, int):
        raise TypeError("a required major version must be an int")
    if major < 0:
        raise ValueError("a required major version must not be negative")


def resolve(registry, requirements):
    queue = deque()
    for name in sorted(requirements):
        _check_major(requirements[name])
        queue.append((name, requirements[name]))
    chosen = {}
    wanted = {}
    while queue:
        name, major = queue.popleft()
        if name in wanted:
            if wanted[name] != major:
                raise ConflictError("%s is required at major %d and %d" % (name, wanted[name], major))
            continue
        if name not in registry:
            raise ResolutionError("unknown package: %s" % (name,))
        version = newest(registry[name], major)
        if version is None:
            raise ResolutionError("no version of %s with major %d" % (name, major))
        wanted[name] = major
        chosen[name] = version
        dependencies = registry[name][version]
        for dependency in sorted(dependencies):
            _check_major(dependencies[dependency])
            queue.append((dependency, dependencies[dependency]))
    return {name: chosen[name] for name in sorted(chosen)}
