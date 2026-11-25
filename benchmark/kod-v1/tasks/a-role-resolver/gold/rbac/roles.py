"""Roles with inheritance; revocations remove inherited allow patterns."""

from rbac.patterns import validate_pattern


def _check_name(name, what):
    if type(name) is not str:
        raise TypeError(what + ' must be a str')
    if not name:
        raise ValueError(what + ' must not be empty')


def _patterns(patterns):
    if type(patterns) not in (list, tuple):
        raise TypeError('patterns must be a list or tuple')
    for pattern in patterns:
        validate_pattern(pattern)
    return frozenset(patterns)


class RoleSet:
    def __init__(self):
        self._allow = {}
        self._deny = {}
        self._revoke = {}
        self._parents = {}
        self._cache = {}

    def add_role(self, name, allow=(), deny=(), revoke=(), inherits=()):
        _check_name(name, 'name')
        if name in self._parents:
            raise ValueError('role already defined: ' + name)
        allow = _patterns(allow)
        deny = _patterns(deny)
        revoke = _patterns(revoke)
        if type(inherits) not in (list, tuple):
            raise TypeError('inherits must be a list or tuple')
        for parent in inherits:
            self._require(parent)
        self._allow[name] = allow
        self._deny[name] = deny
        self._revoke[name] = revoke
        self._parents[name] = list(dict.fromkeys(inherits))
        self._cache.clear()

    def add_inheritance(self, child, parent):
        self._require(child)
        self._require(parent)
        if child == parent or self._inherits_from(parent, child):
            raise ValueError('inheritance cycle')
        if parent not in self._parents[child]:
            self._parents[child].append(parent)
        self._cache.clear()

    def effective(self, name):
        self._require(name)
        if name not in self._cache:
            allow, deny = set(), set()
            for parent in self._parents[name]:
                parent_allow, parent_deny = self.effective(parent)
                allow |= parent_allow
                deny |= parent_deny
            allow -= self._revoke[name]
            allow |= self._allow[name]
            deny |= self._deny[name]
            self._cache[name] = (frozenset(allow), frozenset(deny))
        return self._cache[name]

    def _require(self, name):
        _check_name(name, 'role name')
        if name not in self._parents:
            raise ValueError('unknown role: ' + name)

    def _inherits_from(self, role, ancestor):
        stack, seen = [role], set()
        while stack:
            current = stack.pop()
            if current == ancestor:
                return True
            if current not in seen:
                seen.add(current)
                stack.extend(self._parents[current])
        return False
