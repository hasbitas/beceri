"""Path-scoped allow/deny rules: the deepest matching level decides."""

from acl.paths import join, lineage, split_path

_EFFECTS = ('allow', 'deny')


def _check_action(action):
    if type(action) is not str:
        raise TypeError('action must be a str')
    if not action:
        raise ValueError('action must not be empty')


def _check_principal(principal):
    if type(principal) is not str:
        raise TypeError('principal must be a str')
    if principal == '*':
        return
    kind, _separator, name = principal.partition(':')
    if kind not in ('user', 'group') or not name:
        raise ValueError('bad principal: %r' % principal)


def _check_effect(effect):
    if type(effect) is not str:
        raise TypeError('effect must be a str')
    if effect not in _EFFECTS:
        raise ValueError('effect must be allow or deny')


class Acl:
    def __init__(self, directory):
        self._directory = directory
        self._rules = []

    def grant(self, principal, path, action, effect, recursive=True):
        _check_principal(principal)
        segments = split_path(path)
        _check_action(action)
        _check_effect(effect)
        if type(recursive) is not bool:
            raise TypeError('recursive must be a bool')
        rule = (principal, segments, action, effect, recursive)
        if rule not in self._rules:
            self._rules.append(rule)

    def revoke(self, principal, path, action, effect):
        _check_principal(principal)
        segments = split_path(path)
        _check_action(action)
        _check_effect(effect)
        kept = [rule for rule in self._rules if rule[:4] != (principal, segments, action, effect)]
        removed = len(self._rules) - len(kept)
        self._rules = kept
        return removed

    def decide(self, user, path, action):
        principals = set(self._directory.principals(user))
        principals.add('*')
        segments = split_path(path)
        _check_action(action)
        if action == '*':
            raise ValueError('action must be a concrete action')
        for level in reversed(lineage(segments)):
            effects = {rule[3] for rule in self._rules
                       if rule[1] == level and rule[0] in principals and rule[2] in (action, '*')
                       and (rule[4] or level == segments)}
            if effects:
                effect = 'deny' if 'deny' in effects else 'allow'
                return {'allowed': effect == 'allow', 'path': join(level), 'effect': effect}
        return {'allowed': False, 'path': None, 'effect': None}

    def check(self, user, path, action):
        return self.decide(user, path, action)['allowed']
