"""User role assignments and deny-overrides decisions."""

from rbac.patterns import matches, validate_permission


def _check_user(user):
    if type(user) is not str:
        raise TypeError('user must be a str')
    if not user:
        raise ValueError('user must not be empty')


class Policy:
    def __init__(self, roles):
        self._roles = roles
        self._assigned = {}

    def assign(self, user, role):
        _check_user(user)
        self._roles.effective(role)
        self._assigned.setdefault(user, set()).add(role)

    def unassign(self, user, role):
        _check_user(user)
        if type(role) is not str:
            raise TypeError('role must be a str')
        if role not in self._assigned.get(user, ()):
            raise ValueError('role is not assigned')
        self._assigned[user].discard(role)

    def user_roles(self, user):
        _check_user(user)
        return sorted(self._assigned.get(user, ()))

    def explain(self, user, permission):
        _check_user(user)
        validate_permission(permission)
        for role in sorted(self._assigned.get(user, ())):
            role_allow, role_deny = self._roles.effective(role)
            denied = sorted(p for p in role_deny if matches(p, permission))
            if denied:
                return {'allowed': False, 'decision': 'deny', 'by': denied}
            allowed = sorted(p for p in role_allow if matches(p, permission))
            if allowed:
                return {'allowed': True, 'decision': 'allow', 'by': allowed}
        return {'allowed': False, 'decision': 'default', 'by': []}

    def is_allowed(self, user, permission):
        return self.explain(user, permission)['allowed']
