import unittest

from rbac.patterns import matches, validate_pattern, validate_permission
from rbac.policy import Policy
from rbac.roles import RoleSet


class HiddenRbacTests(unittest.TestCase):
    def test_wildcard_semantics(self):
        self.assertTrue(matches('doc:**', 'doc:read'))
        self.assertTrue(matches('doc:**', 'doc:read:all'))
        self.assertFalse(matches('doc:**', 'doc'))
        self.assertFalse(matches('doc:**', 'file:read'))
        self.assertTrue(matches('**', 'a'))
        self.assertTrue(matches('**', 'a:b:c'))
        self.assertTrue(matches('*:read', 'doc:read'))
        self.assertFalse(matches('*:read', 'doc:write'))
        self.assertFalse(matches('*:*', 'a:b:c'))
        self.assertTrue(matches('*', 'a'))
        self.assertFalse(matches('*', 'a:b'))
        self.assertTrue(matches('a:*:c', 'a:b:c'))
        self.assertFalse(matches('a:*:c', 'a:b:d'))
        self.assertTrue(matches('a:*:**', 'a:b:c'))
        self.assertFalse(matches('a:*:**', 'a:b'))
        self.assertTrue(matches('doc:read', 'doc:read'))
        self.assertFalse(matches('doc:read', 'doc:write'))

    def test_pattern_and_permission_validation(self):
        for bad in ('', 'a::b', ':a', 'a:', 'a:**:b', '***', 'a*:b', 'a b', 'Doc:read', 'a.b', '**:a', 'a:*b'):
            with self.assertRaises(ValueError, msg=repr(bad)):
                validate_pattern(bad)
        for good in ('a', '*', '**', 'a:*', 'a:**', '*:*:**', 'x_y:z-1'):
            validate_pattern(good)
        for bad in (None, 5, b'a', ['a']):
            with self.assertRaises(TypeError, msg=repr(bad)):
                validate_pattern(bad)
            with self.assertRaises(TypeError, msg=repr(bad)):
                validate_permission(bad)
        for bad in ('', 'a:*', 'a:**', 'a::b', 'A:b', 'a:b:'):
            with self.assertRaises(ValueError, msg=repr(bad)):
                validate_permission(bad)
        validate_permission('a:b-c:d_9')
        with self.assertRaises(ValueError):
            matches('bad pattern', 'a:b')
        with self.assertRaises(ValueError):
            matches('a:*', 'a:*')
        with self.assertRaises(ValueError):
            matches('a::', 'a:*')
        with self.assertRaises(TypeError):
            matches(None, 'a')

    def test_revoke_semantics_and_diamond(self):
        roles = RoleSet()
        roles.add_role('base', allow=['doc:read', 'doc:write'], deny=['sys:halt'])
        roles.add_role('left', revoke=['doc:write'], inherits=['base'])
        roles.add_role('right', inherits=['base'])
        roles.add_role('top', inherits=['left', 'right'])
        self.assertEqual(roles.effective('left')[0], frozenset({'doc:read'}))
        self.assertEqual(roles.effective('top')[0], frozenset({'doc:read', 'doc:write'}))
        roles.add_role('chain', revoke=['doc:write'], inherits=['left'])
        self.assertEqual(roles.effective('chain')[0], frozenset({'doc:read'}))
        roles.add_role('wild', allow=['doc:*'])
        roles.add_role('mid', revoke=['doc:read'], inherits=['wild'])
        self.assertEqual(roles.effective('mid')[0], frozenset({'doc:*'}))
        roles.add_role('own', allow=['x:y'], revoke=['x:y', 'doc:read'], inherits=['base'])
        self.assertEqual(roles.effective('own')[0], frozenset({'x:y', 'doc:write'}))
        roles.add_role('nodeny', revoke=['sys:halt'], inherits=['base'])
        self.assertEqual(roles.effective('nodeny')[1], frozenset({'sys:halt'}))
        roles.add_role('later', allow=['sys:halt'], inherits=['base'])
        self.assertEqual(roles.effective('later')[1], frozenset({'sys:halt'}))
        self.assertIsInstance(roles.effective('top')[0], frozenset)
        self.assertIsInstance(roles.effective('top')[1], frozenset)

    def test_edges_added_later_are_visible(self):
        roles = RoleSet()
        roles.add_role('a', allow=['x:one'])
        roles.add_role('b', allow=['x:two'])
        roles.add_role('c', allow=['x:three'], inherits=['b'])
        policy = Policy(roles)
        policy.assign('u', 'c')
        self.assertEqual(roles.effective('c')[0], frozenset({'x:two', 'x:three'}))
        self.assertFalse(policy.is_allowed('u', 'x:one'))
        roles.add_inheritance('b', 'a')
        self.assertTrue(policy.is_allowed('u', 'x:one'))
        self.assertEqual(roles.effective('c')[0], frozenset({'x:one', 'x:two', 'x:three'}))
        roles.add_inheritance('b', 'a')
        self.assertEqual(roles.effective('b')[0], frozenset({'x:one', 'x:two'}))
        roles.add_role('d', deny=['x:one'])
        roles.add_inheritance('c', 'd')
        self.assertFalse(policy.is_allowed('u', 'x:one'))
        self.assertEqual(roles.effective('c')[1], frozenset({'x:one'}))

    def test_inheritance_validation_and_cycles(self):
        roles = RoleSet()
        roles.add_role('a')
        roles.add_role('b', inherits=['a'])
        roles.add_role('c', inherits=['b'])
        for child, parent in (('a', 'a'), ('a', 'b'), ('a', 'c'), ('b', 'c')):
            with self.assertRaises(ValueError, msg=(child, parent)):
                roles.add_inheritance(child, parent)
        with self.assertRaises(ValueError):
            roles.add_inheritance('zzz', 'a')
        with self.assertRaises(ValueError):
            roles.add_inheritance('a', 'zzz')
        with self.assertRaises(ValueError):
            roles.add_inheritance('', 'a')
        with self.assertRaises(TypeError):
            roles.add_inheritance(1, 'zzz')
        with self.assertRaises(ValueError):
            roles.add_inheritance('zzz', 5)
        with self.assertRaises(TypeError):
            roles.add_inheritance('a', 5)
        roles.add_inheritance('c', 'a')
        roles.add_inheritance('c', 'b')
        roles.add_role('d')
        roles.add_inheritance('a', 'd')
        with self.assertRaises(ValueError):
            roles.add_inheritance('d', 'c')

    def test_add_role_validation_order_and_atomicity(self):
        roles = RoleSet()
        roles.add_role('base', allow=['a:b'])
        cases = [
            (TypeError, dict(name=5, allow=['bad pattern'])),
            (ValueError, dict(name='')),
            (ValueError, dict(name='base', allow=5)),
            (TypeError, dict(name='x', allow='a:b')),
            (TypeError, dict(name='x', allow=['a:b', 5])),
            (ValueError, dict(name='x', allow=['a:b', 'bad pattern'], deny=5)),
            (TypeError, dict(name='x', deny=5, revoke=['bad pattern'])),
            (ValueError, dict(name='x', deny=['A:b'])),
            (ValueError, dict(name='x', revoke=['a::b'])),
            (TypeError, dict(name='x', revoke=['a:b'], inherits='base')),
            (ValueError, dict(name='x', inherits=['base', 'nope'])),
            (TypeError, dict(name='x', inherits=['base', 7])),
            (ValueError, dict(name='x', inherits=['x'])),
            (ValueError, dict(name='x', inherits=[''])),
        ]
        for error, kwargs in cases:
            with self.assertRaises(error, msg=kwargs):
                roles.add_role(**kwargs)
        with self.assertRaises(ValueError):
            roles.effective('x')
        with self.assertRaises(TypeError):
            roles.effective(None)
        with self.assertRaises(ValueError):
            roles.effective('')
        roles.add_role('x', allow=('p:q', 'p:q'), inherits=('base', 'base'))
        self.assertEqual(roles.effective('x')[0], frozenset({'a:b', 'p:q'}))

    def test_explain_shapes_and_sorting(self):
        roles = RoleSet()
        roles.add_role('big', allow=['doc:read', 'doc:*', '**', 'zzz:read'])
        roles.add_role('blocker', deny=['doc:**', 'doc:read', '*:read'])
        policy = Policy(roles)
        self.assertEqual(policy.explain('nobody', 'doc:read'), {'allowed': False, 'decision': 'default', 'by': []})
        policy.assign('u', 'big')
        self.assertEqual(policy.explain('u', 'doc:read'),
                         {'allowed': True, 'decision': 'allow', 'by': ['**', 'doc:*', 'doc:read']})
        self.assertEqual(policy.explain('u', 'other:thing'), {'allowed': True, 'decision': 'allow', 'by': ['**']})
        policy.assign('u', 'blocker')
        self.assertEqual(policy.explain('u', 'doc:read'),
                         {'allowed': False, 'decision': 'deny', 'by': ['*:read', 'doc:**', 'doc:read']})
        self.assertEqual(policy.explain('u', 'doc:write'),
                         {'allowed': False, 'decision': 'deny', 'by': ['doc:**']})
        self.assertEqual(policy.explain('u', 'zzz:read'),
                         {'allowed': False, 'decision': 'deny', 'by': ['*:read']})
        self.assertEqual(policy.explain('u', 'zzz:write'),
                         {'allowed': True, 'decision': 'allow', 'by': ['**']})

    def test_parent_deny_cannot_be_overridden_by_child_allow(self):
        roles = RoleSet()
        roles.add_role('base', deny=['db:drop'])
        roles.add_role('admin', allow=['db:**'], inherits=['base'])
        policy = Policy(roles)
        policy.assign('root', 'admin')
        self.assertTrue(policy.is_allowed('root', 'db:select'))
        self.assertFalse(policy.is_allowed('root', 'db:drop'))
        self.assertEqual(policy.explain('root', 'db:drop')['decision'], 'deny')
        self.assertFalse(policy.is_allowed('root', 'db'))

    def test_assignment_management(self):
        roles = RoleSet()
        roles.add_role('r1', allow=['a:b'])
        roles.add_role('r2', allow=['c:d'])
        policy = Policy(roles)
        policy.assign('u', 'r2')
        policy.assign('u', 'r1')
        policy.assign('u', 'r1')
        listing = policy.user_roles('u')
        self.assertEqual(listing, ['r1', 'r2'])
        listing.append('junk')
        self.assertEqual(policy.user_roles('u'), ['r1', 'r2'])
        self.assertEqual(policy.user_roles('ghost'), [])
        policy.unassign('u', 'r1')
        self.assertFalse(policy.is_allowed('u', 'a:b'))
        self.assertTrue(policy.is_allowed('u', 'c:d'))
        with self.assertRaises(ValueError):
            policy.unassign('u', 'r1')
        with self.assertRaises(ValueError):
            policy.unassign('ghost', 'r1')
        with self.assertRaises(TypeError):
            policy.unassign('u', 5)
        with self.assertRaises(ValueError):
            policy.assign('u', 'missing')
        with self.assertRaises(TypeError):
            policy.assign('u', None)
        with self.assertRaises(ValueError):
            policy.assign('', 'r1')
        with self.assertRaises(TypeError):
            policy.assign(None, 'missing')
        with self.assertRaises(ValueError):
            policy.user_roles('')
        with self.assertRaises(TypeError):
            policy.user_roles(3)
        with self.assertRaises(ValueError):
            policy.is_allowed('u', 'a:*')
        with self.assertRaises(TypeError):
            policy.is_allowed('u', None)
        with self.assertRaises(TypeError):
            policy.explain(1, '')
        with self.assertRaises(ValueError):
            policy.explain('', 5)
        self.assertEqual(policy.user_roles('u'), ['r2'])
