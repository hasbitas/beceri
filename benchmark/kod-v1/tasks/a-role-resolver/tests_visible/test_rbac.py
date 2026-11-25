import unittest

from rbac.patterns import matches
from rbac.policy import Policy
from rbac.roles import RoleSet


class VisibleRbacTests(unittest.TestCase):
    def test_inherited_permissions(self):
        roles = RoleSet()
        roles.add_role('viewer', allow=['doc:read'])
        roles.add_role('editor', allow=['doc:write'], inherits=['viewer'])
        policy = Policy(roles)
        policy.assign('alice', 'editor')
        self.assertTrue(policy.is_allowed('alice', 'doc:read'))
        self.assertTrue(policy.is_allowed('alice', 'doc:write'))
        self.assertFalse(policy.is_allowed('alice', 'doc:delete'))
        self.assertEqual(roles.effective('editor'), (frozenset({'doc:read', 'doc:write'}), frozenset()))
        self.assertTrue(matches('doc:*', 'doc:read'))
        self.assertFalse(matches('doc:*', 'doc:read:all'))

    def test_deny_overrides_allow_across_roles(self):
        roles = RoleSet()
        roles.add_role('a-allow', allow=['doc:*'])
        roles.add_role('z-block', deny=['doc:delete'])
        policy = Policy(roles)
        policy.assign('bob', 'a-allow')
        policy.assign('bob', 'z-block')
        self.assertFalse(policy.is_allowed('bob', 'doc:delete'))
        self.assertTrue(policy.is_allowed('bob', 'doc:read'))
        self.assertEqual(policy.explain('bob', 'doc:delete'),
                         {'allowed': False, 'decision': 'deny', 'by': ['doc:delete']})
        self.assertEqual(policy.user_roles('bob'), ['a-allow', 'z-block'])

    def test_rejects_bad_input(self):
        roles = RoleSet()
        roles.add_role('base', allow=['x:y'])
        with self.assertRaises(ValueError):
            roles.add_role('base')
        with self.assertRaises(ValueError):
            roles.add_role('other', inherits=['missing'])
        with self.assertRaises(ValueError):
            roles.add_inheritance('base', 'base')
        with self.assertRaises(ValueError):
            matches('a::b', 'a:b')
        with self.assertRaises(TypeError):
            Policy(roles).assign(3, 'base')
