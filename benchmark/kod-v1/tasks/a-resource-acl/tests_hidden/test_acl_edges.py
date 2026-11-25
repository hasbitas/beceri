import unittest

from acl.acl import Acl
from acl.groups import Directory
from acl.paths import join, lineage, split_path


class HiddenAclTests(unittest.TestCase):
    def test_split_path_normalization(self):
        self.assertEqual(split_path('/'), ())
        self.assertEqual(split_path('/a'), ('a',))
        self.assertEqual(split_path('/a/b/'), ('a', 'b'))
        self.assertEqual(split_path('/a/b'), ('a', 'b'))
        self.assertEqual(split_path('/a b/c.d/..e'), ('a b', 'c.d', '..e'))
        for bad in ('', 'a', 'a/b', '//', '//a', '/a//b', '/a//', '/./a', '/a/..', '/a/./b', '/../a', '///'):
            with self.assertRaises(ValueError, msg=repr(bad)):
                split_path(bad)
        for bad in (None, 5, b'/a', ('a',)):
            with self.assertRaises(TypeError, msg=repr(bad)):
                split_path(bad)

    def test_lineage_and_join(self):
        self.assertEqual(lineage(()), [()])
        self.assertEqual(lineage(('a', 'b', 'c')), [(), ('a',), ('a', 'b'), ('a', 'b', 'c')])
        self.assertEqual(join(()), '/')
        self.assertEqual(join(('a', 'b')), '/a/b')
        self.assertEqual(join(split_path('/x/y/')), '/x/y')

    def test_nested_groups_are_transitive(self):
        directory = Directory()
        directory.add_user('g1', 'u')
        directory.add_subgroup('g2', 'g1')
        directory.add_subgroup('g3', 'g2')
        directory.add_subgroup('g4', 'g3')
        self.assertEqual(directory.principals('u'),
                         frozenset({'user:u', 'group:g1', 'group:g2', 'group:g3', 'group:g4'}))
        directory.add_user('base', 'v')
        directory.add_subgroup('left', 'base')
        directory.add_subgroup('right', 'base')
        directory.add_subgroup('top', 'left')
        directory.add_subgroup('top', 'right')
        self.assertEqual(directory.principals('v'),
                         frozenset({'user:v', 'group:base', 'group:left', 'group:right', 'group:top'}))
        self.assertEqual(directory.principals('nobody'), frozenset({'user:nobody'}))
        self.assertEqual(directory.principals('g1'), frozenset({'user:g1'}))
        self.assertIsInstance(directory.principals('u'), frozenset)

    def test_group_cycles_are_rejected_atomically(self):
        directory = Directory()
        directory.add_subgroup('B', 'A')
        directory.add_subgroup('C', 'B')
        directory.add_subgroup('C', 'B')
        for parent, child in (('A', 'A'), ('A', 'C'), ('A', 'B'), ('B', 'C')):
            with self.assertRaises(ValueError, msg=(parent, child)):
                directory.add_subgroup(parent, child)
        directory.add_user('A', 'u')
        self.assertEqual(directory.principals('u'), frozenset({'user:u', 'group:A', 'group:B', 'group:C'}))
        directory.add_subgroup('A', 'D')
        directory.add_user('D', 'w')
        self.assertEqual(directory.principals('w'),
                         frozenset({'user:w', 'group:D', 'group:A', 'group:B', 'group:C'}))
        with self.assertRaises(ValueError):
            directory.add_subgroup('D', 'C')

    def test_directory_validation(self):
        directory = Directory()
        for call, error in (
            (lambda: directory.add_user(1, 'u'), TypeError),
            (lambda: directory.add_user('', 'u'), ValueError),
            (lambda: directory.add_user('g', None), TypeError),
            (lambda: directory.add_user('g', ''), ValueError),
            (lambda: directory.add_user('', 5), ValueError),
            (lambda: directory.add_subgroup(None, 'c'), TypeError),
            (lambda: directory.add_subgroup('p', ''), ValueError),
            (lambda: directory.add_subgroup('', 3), ValueError),
            (lambda: directory.add_subgroup('p', 3), TypeError),
            (lambda: directory.principals(''), ValueError),
            (lambda: directory.principals(7), TypeError),
        ):
            with self.assertRaises(error):
                call()
        self.assertEqual(directory.principals('u'), frozenset({'user:u'}))

    def test_deepest_level_decides_and_deny_wins_ties(self):
        directory = Directory()
        directory.add_user('staff', 'alice')
        directory.add_user('staff', 'bob')
        acl = Acl(directory)
        acl.grant('group:staff', '/docs', 'read', 'allow')
        acl.grant('user:bob', '/docs/secret', 'read', 'deny')
        acl.grant('user:alice', '/docs/secret/memo', 'read', 'allow')
        self.assertEqual(acl.decide('bob', '/docs/secret/memo', 'read'),
                         {'allowed': False, 'path': '/docs/secret', 'effect': 'deny'})
        self.assertEqual(acl.decide('alice', '/docs/secret/memo/', 'read'),
                         {'allowed': True, 'path': '/docs/secret/memo', 'effect': 'allow'})
        self.assertEqual(acl.decide('alice', '/docs/secret/other', 'read'),
                         {'allowed': True, 'path': '/docs', 'effect': 'allow'})
        self.assertEqual(acl.decide('carol', '/docs', 'read'), {'allowed': False, 'path': None, 'effect': None})
        first = Acl(directory)
        first.grant('user:alice', '/x', 'read', 'allow')
        first.grant('group:staff', '/x', 'read', 'deny')
        second = Acl(directory)
        second.grant('group:staff', '/x', 'read', 'deny')
        second.grant('user:alice', '/x', 'read', 'allow')
        for acl_under_test in (first, second):
            self.assertEqual(acl_under_test.decide('alice', '/x/y', 'read'),
                             {'allowed': False, 'path': '/x', 'effect': 'deny'})
        deeper = Acl(directory)
        deeper.grant('group:staff', '/x', 'read', 'deny')
        deeper.grant('user:alice', '/x/y/z', 'read', 'allow')
        self.assertTrue(deeper.check('alice', '/x/y/z', 'read'))
        self.assertTrue(deeper.check('alice', '/x/y/z/w', 'read'))
        self.assertFalse(deeper.check('alice', '/x/y', 'read'))

    def test_non_recursive_rules_apply_only_to_their_own_path(self):
        directory = Directory()
        acl = Acl(directory)
        acl.grant('*', '/pub', 'read', 'allow', recursive=False)
        self.assertTrue(acl.check('anyone', '/pub', 'read'))
        self.assertTrue(acl.check('anyone', '/pub/', 'read'))
        self.assertFalse(acl.check('anyone', '/pub/x', 'read'))
        acl.grant('user:dan', '/docs', 'read', 'deny', recursive=False)
        acl.grant('user:dan', '/', 'read', 'allow')
        self.assertFalse(acl.check('dan', '/docs', 'read'))
        self.assertTrue(acl.check('dan', '/docs/a', 'read'))
        self.assertEqual(acl.decide('dan', '/docs/a', 'read'), {'allowed': True, 'path': '/', 'effect': 'allow'})
        self.assertEqual(acl.decide('dan', '/', 'read'), {'allowed': True, 'path': '/', 'effect': 'allow'})
        acl.grant('user:dan', '/docs/a', 'read', 'deny', recursive=False)
        self.assertFalse(acl.check('dan', '/docs/a', 'read'))
        self.assertTrue(acl.check('dan', '/docs/a/b', 'read'))

    def test_wildcard_action_and_principal(self):
        directory = Directory()
        directory.add_user('g', 'eve')
        acl = Acl(directory)
        acl.grant('user:eve', '/x', '*', 'allow')
        self.assertTrue(acl.check('eve', '/x/y', 'write'))
        self.assertTrue(acl.check('eve', '/x', 'read'))
        acl.grant('user:eve', '/x', 'write', 'deny')
        self.assertFalse(acl.check('eve', '/x/y', 'write'))
        self.assertTrue(acl.check('eve', '/x/y', 'read'))
        acl.grant('group:g', '/x/y', 'write', 'allow')
        self.assertTrue(acl.check('eve', '/x/y', 'write'))
        self.assertFalse(acl.check('eve', '/x', 'write'))
        acl.grant('*', '/open', 'read', 'allow')
        self.assertTrue(acl.check('stranger', '/open/deep/er', 'read'))
        self.assertFalse(acl.check('stranger', '/open/deep', 'write'))
        acl.grant('user:stranger', '/open/deep', 'read', 'deny')
        self.assertFalse(acl.check('stranger', '/open/deep/er', 'read'))
        self.assertTrue(acl.check('eve', '/open/deep/er', 'read'))

    def test_nested_group_rules_and_root_rule(self):
        directory = Directory()
        directory.add_user('g1', 'u')
        directory.add_subgroup('g2', 'g1')
        directory.add_subgroup('g3', 'g2')
        acl = Acl(directory)
        acl.grant('group:g3', '/vault', 'read', 'allow')
        acl.grant('group:g1', '/', 'read', 'deny')
        self.assertTrue(acl.check('u', '/vault/x', 'read'))
        self.assertFalse(acl.check('u', '/elsewhere', 'read'))
        self.assertEqual(acl.decide('u', '/elsewhere', 'read'), {'allowed': False, 'path': '/', 'effect': 'deny'})
        self.assertEqual(acl.decide('u', '/', 'read'), {'allowed': False, 'path': '/', 'effect': 'deny'})

    def test_revoke_normalizes_and_counts(self):
        directory = Directory()
        acl = Acl(directory)
        acl.grant('user:a', '/x', 'read', 'allow')
        acl.grant('user:a', '/x', 'read', 'allow')
        acl.grant('user:a', '/x', 'read', 'allow', recursive=False)
        acl.grant('user:a', '/x', 'read', 'deny')
        acl.grant('user:a', '/x', 'write', 'allow')
        self.assertEqual(acl.revoke('user:a', '/x/', 'read', 'allow'), 2)
        self.assertEqual(acl.revoke('user:a', '/x', 'read', 'allow'), 0)
        self.assertFalse(acl.check('a', '/x', 'read'))
        self.assertEqual(acl.revoke('user:a', '/x', 'read', 'deny'), 1)
        self.assertEqual(acl.decide('a', '/x/y', 'read'), {'allowed': False, 'path': None, 'effect': None})
        self.assertTrue(acl.check('a', '/x/y', 'write'))
        with self.assertRaises(ValueError):
            acl.revoke('a', '/x', 'read', 'allow')
        with self.assertRaises(ValueError):
            acl.revoke('user:a', 'x', 'read', 'allow')
        with self.assertRaises(TypeError):
            acl.revoke('user:a', '/x', 5, 'allow')
        with self.assertRaises(ValueError):
            acl.revoke('user:a', '/x', 'read', 'permit')
        self.assertTrue(acl.check('a', '/x/y', 'write'))

    def test_grant_validation_order_and_atomicity(self):
        acl = Acl(Directory())
        cases = [
            (ValueError, ('bob', 'bad', 5, 5)),
            (TypeError, (5, 'bad', 'r', 'allow')),
            (ValueError, ('bob', 'bad', 'r', 'allow')),
            (ValueError, ('user:', '/a', 'r', 'allow')),
            (ValueError, ('group:', '/a', 'r', 'allow')),
            (ValueError, ('team:x', '/a', 'r', 'allow')),
            (ValueError, ('', '/a', 'r', 'allow')),
            (ValueError, ('*', 'bad', 5, 5)),
            (TypeError, ('*', 5, 'r', 'allow')),
            (ValueError, ('*', '//a', 'r', 'allow')),
            (TypeError, ('*', '/a', 5, 5)),
            (ValueError, ('*', '/a', '', 5)),
            (TypeError, ('*', '/a', 'r', 5)),
            (ValueError, ('*', '/a', 'r', 'maybe')),
        ]
        for error, args in cases:
            with self.assertRaises(error, msg=args):
                acl.grant(*args)
        with self.assertRaises(ValueError):
            acl.grant('*', '/a', 'r', 'maybe', recursive=1)
        with self.assertRaises(TypeError):
            acl.grant('*', '/a', 'r', 'allow', 1)
        with self.assertRaises(TypeError):
            acl.grant('*', '/a', 'r', 'allow', recursive=None)
        self.assertFalse(acl.check('x', '/a', 'r'))
        acl.grant('*', '/a', 'r', 'allow', False)
        self.assertTrue(acl.check('x', '/a', 'r'))

    def test_check_validation_order(self):
        acl = Acl(Directory())
        cases = [
            (TypeError, (5, 'bad', 5)),
            (ValueError, ('', 'bad', 5)),
            (ValueError, ('u', 'bad', 5)),
            (TypeError, ('u', None, 5)),
            (TypeError, ('u', '/a', 5)),
            (ValueError, ('u', '/a', '')),
            (ValueError, ('u', '/a', '*')),
            (ValueError, ('u', '/a//b', 'r')),
        ]
        for error, args in cases:
            with self.assertRaises(error, msg=args):
                acl.check(*args)
            with self.assertRaises(error, msg=args):
                acl.decide(*args)
        self.assertEqual(acl.decide('u', '/', 'r'), {'allowed': False, 'path': None, 'effect': None})
