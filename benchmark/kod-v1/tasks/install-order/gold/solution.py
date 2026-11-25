"""Deterministic dependency ordering."""
import heapq


def install_order(packages):
    if not isinstance(packages, dict):
        raise TypeError('packages must be a dict')
    dependencies = {}
    for name, items in packages.items():
        if not isinstance(name, str):
            raise TypeError('package names must be strings')
        if not name:
            raise ValueError('empty package name')
        if not isinstance(items, (list, tuple)):
            raise TypeError('dependencies must be lists or tuples')
        unique = set()
        for dependency in items:
            if not isinstance(dependency, str):
                raise TypeError('dependency names must be strings')
            if not dependency:
                raise ValueError('empty dependency name')
            unique.add(dependency)
        dependencies[name] = unique

    missing = sorted((name, dep) for name, deps in dependencies.items()
                     for dep in deps if dep not in dependencies)
    if missing:
        raise ValueError('missing dependencies: ' + '; '.join(
            name + ' -> ' + dep for name, dep in missing))

    dependents = {name: [] for name in dependencies}
    remaining = {name: len(deps) for name, deps in dependencies.items()}
    for name, deps in dependencies.items():
        for dep in deps:
            dependents[dep].append(name)
    ready = [name for name, count in remaining.items() if count == 0]
    heapq.heapify(ready)
    result = []
    while ready:
        name = heapq.heappop(ready)
        result.append(name)
        del remaining[name]
        for dependent in dependents[name]:
            remaining[dependent] -= 1
            if remaining[dependent] == 0:
                heapq.heappush(ready, dependent)
    if remaining:
        raise ValueError('cycle blocks: ' + ', '.join(sorted(remaining)))
    return result
