"""Users and nested groups."""


def _check(value, what):
    if type(value) is not str:
        raise TypeError(what + ' must be a str')
    if not value:
        raise ValueError(what + ' must not be empty')


class Directory:
    def __init__(self):
        self._user_groups = {}
        self._parents = {}

    def add_user(self, group, user):
        _check(group, 'group')
        _check(user, 'user')
        self._parents.setdefault(group, set())
        self._user_groups.setdefault(user, set()).add(group)

    def add_subgroup(self, parent, child):
        _check(parent, 'parent')
        _check(child, 'child')
        if child == parent or child in self._parents.get(parent, ()):
            raise ValueError('group cycle')
        self._parents.setdefault(parent, set())
        self._parents.setdefault(child, set()).add(parent)

    def principals(self, user):
        _check(user, 'user')
        found = {'user:' + user}
        for group in self._user_groups.get(user, ()):
            found.add('group:' + group)
            found.update('group:' + name for name in self._containing(group))
        return frozenset(found)

    def _containing(self, group):
        seen = set()
        stack = list(self._parents.get(group, ()))
        while stack:
            current = stack.pop()
            if current not in seen:
                seen.add(current)
                stack.extend(self._parents.get(current, ()))
        return seen
